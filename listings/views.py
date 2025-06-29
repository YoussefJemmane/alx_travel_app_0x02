from django.shortcuts import render
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer
from django.db import models
import requests
import uuid
import logging
from .tasks import send_payment_confirmation_email

# Create your views here.

class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing listings.
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing bookings.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter bookings to show only those related to the current user
        (either as guest or as listing owner)
        """
        user = self.request.user
        return Booking.objects.filter(
            models.Q(guest=user) | 
            models.Q(listing__owner=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(guest=self.request.user)

    @action(detail=True, methods=['post'], url_path='initiate-payment')
    def initiate_payment(self, request, pk=None):
        """
        Initiate payment for a booking using Chapa API
        """
        booking = self.get_object()
        
        # Check if user is the booking owner
        if booking.guest != request.user:
            return Response(
                {'error': 'You can only initiate payment for your own bookings'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if booking already has a pending or completed payment
        existing_payment = Payment.objects.filter(
            booking=booking,
            status__in=['PENDING', 'COMPLETED']
        ).first()
        
        if existing_payment:
            return Response(
                {'error': 'Payment already exists for this booking',
                 'payment_id': existing_payment.id,
                 'status': existing_payment.status},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create payment record
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_price,
            status='PENDING',
            transaction_id=f"TXN_{uuid.uuid4().hex[:10].upper()}"
        )
        
        # Prepare Chapa payment request
        chapa_data = {
            "amount": str(booking.total_price),
            "currency": "ETB",
            "email": request.user.email,
            "first_name": request.user.first_name or request.user.username,
            "last_name": request.user.last_name or "",
            "phone_number": "0911234567",  # You might want to add this to user model
            "tx_ref": str(payment.reference),
            "callback_url": f"{request.build_absolute_uri('/api/bookings/')}{booking.id}/verify-payment/",
            "return_url": f"{request.build_absolute_uri('/api/bookings/')}{booking.id}/payment-success/",
            "customization": {
                "title": f"Payment for {booking.listing.title}",
                "description": f"Booking from {booking.check_in_date} to {booking.check_out_date}"
            }
        }
        
        try:
            # Make request to Chapa API
            headers = {
                'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                'https://api.chapa.co/v1/transaction/initialize',
                json=chapa_data,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            chapa_response = response.json()
            
            if chapa_response.get('status') == 'success':
                # Update payment with Chapa transaction ID
                payment.transaction_id = chapa_response['data']['tx_ref']
                payment.save()
                
                return Response({
                    'status': 'success',
                    'payment_id': payment.id,
                    'checkout_url': chapa_response['data']['checkout_url'],
                    'tx_ref': chapa_response['data']['tx_ref']
                })
            else:
                payment.status = 'FAILED'
                payment.save()
                return Response(
                    {'error': 'Payment initialization failed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except requests.RequestException as e:
            logging.error(f"Chapa API error: {e}")
            payment.status = 'FAILED'
            payment.save()
            return Response(
                {'error': 'Payment service unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    @action(detail=True, methods=['post'], url_path='verify-payment')
    def verify_payment(self, request, pk=None):
        """
        Verify payment status with Chapa API
        """
        booking = self.get_object()
        tx_ref = request.data.get('tx_ref')
        
        if not tx_ref:
            return Response(
                {'error': 'Transaction reference is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get payment record
            payment = Payment.objects.get(
                booking=booking,
                reference=tx_ref
            )
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Verify with Chapa API
            headers = {
                'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
            }
            
            response = requests.get(
                f'https://api.chapa.co/v1/transaction/verify/{tx_ref}',
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            chapa_response = response.json()
            
            if chapa_response.get('status') == 'success':
                payment_status = chapa_response['data']['status']
                
                if payment_status == 'success':
                    payment.status = 'COMPLETED'
                    booking.status = 'CONFIRMED'
                    booking.save()
                    payment.save()
                    
                    # Send confirmation email asynchronously
                    send_payment_confirmation_email.delay(
                        booking.guest.email,
                        booking.guest.first_name or booking.guest.username,
                        booking.listing.title,
                        str(booking.total_price)
                    )
                    
                    return Response({
                        'status': 'success',
                        'payment_status': 'COMPLETED',
                        'booking_status': 'CONFIRMED'
                    })
                else:
                    payment.status = 'FAILED'
                    payment.save()
                    return Response({
                        'status': 'failed',
                        'payment_status': 'FAILED'
                    })
            else:
                return Response(
                    {'error': 'Payment verification failed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except requests.RequestException as e:
            logging.error(f"Chapa verification error: {e}")
            return Response(
                {'error': 'Payment verification service unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    @action(detail=True, methods=['get'], url_path='payment-success')
    def payment_success(self, request, pk=None):
        """
        Handle successful payment redirect
        """
        booking = self.get_object()
        return Response({
            'message': 'Payment completed successfully',
            'booking_id': booking.id,
            'status': booking.status
        })


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing payment information
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter payments to show only those related to the current user
        """
        user = self.request.user
        return Payment.objects.filter(
            models.Q(booking__guest=user) | 
            models.Q(booking__listing__owner=user)
        ).distinct()
