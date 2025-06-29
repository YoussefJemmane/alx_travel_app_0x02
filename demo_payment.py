#!/usr/bin/env python
"""
Demo script showing Chapa payment integration workflow
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app.settings')
sys.path.append('/home/joemane/ALX/Backend-ProDev/alx_travel_app_0x02/alx_travel_app')

django.setup()

from django.contrib.auth.models import User
from listings.models import Listing, Booking, Payment

def demo_payment_workflow():
    """
    Demonstrate the complete payment workflow
    """
    print("=== ALX Travel App - Chapa Payment Integration Demo ===\n")
    
    # 1. Create sample data
    print("1. Creating sample data...")
    try:
        # Create a user (property owner)
        owner = User.objects.create_user(
            username='property_owner',
            email='owner@example.com',
            first_name='John',
            last_name='Doe'
        )
        
        # Create a guest user
        guest = User.objects.create_user(
            username='guest_user',
            email='guest@example.com',
            first_name='Jane',
            last_name='Smith'
        )
        
        # Create a listing
        listing = Listing.objects.create(
            owner=owner,
            title='Beautiful Lake House',
            description='A stunning lake house with amazing views',
            price=150.00,
            location='Lake Victoria, Kenya',
            capacity=4,
            amenities='WiFi, Kitchen, Parking, Lake View',
            is_available=True
        )
        
        # Create a booking
        booking = Booking.objects.create(
            listing=listing,
            guest=guest,
            check_in_date=date(2024, 7, 15),
            check_out_date=date(2024, 7, 17),
            guests_count=2,
            status='PENDING'
        )
        
        print(f"✓ Created listing: {listing.title}")
        print(f"✓ Created booking for {guest.username}")
        print(f"✓ Booking total: ETB {booking.total_price}")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        return
    
    # 2. Demonstrate payment creation
    print("\n2. Creating payment record...")
    try:
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_price,
            status='PENDING',
            transaction_id=f"TXN_DEMO_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        print(f"✓ Payment created with ID: {payment.id}")
        print(f"✓ Payment reference: {payment.reference}")
        print(f"✓ Transaction ID: {payment.transaction_id}")
        print(f"✓ Amount: ETB {payment.amount}")
        print(f"✓ Status: {payment.status}")
        
    except Exception as e:
        print(f"Error creating payment: {e}")
        return
    
    # 3. Simulate Chapa API request
    print("\n3. Simulating Chapa API integration...")
    
    chapa_payload = {
        "amount": str(payment.amount),
        "currency": "ETB",
        "email": guest.email,
        "first_name": guest.first_name,
        "last_name": guest.last_name,
        "phone_number": "0911234567",
        "tx_ref": str(payment.reference),
        "callback_url": f"http://localhost:8000/api/bookings/{booking.id}/verify-payment/",
        "return_url": f"http://localhost:8000/api/bookings/{booking.id}/payment-success/",
        "customization": {
            "title": f"Payment for {listing.title}",
            "description": f"Booking from {booking.check_in_date} to {booking.check_out_date}"
        }
    }
    
    print("Chapa API Payload:")
    print(json.dumps(chapa_payload, indent=2))
    
    # 4. Simulate successful payment
    print("\n4. Simulating successful payment verification...")
    try:
        # Update payment status as if verification was successful
        payment.status = 'COMPLETED'
        payment.save()
        
        # Update booking status
        booking.status = 'CONFIRMED'
        booking.save()
        
        print(f"✓ Payment status updated to: {payment.status}")
        print(f"✓ Booking status updated to: {booking.status}")
        
    except Exception as e:
        print(f"Error updating payment status: {e}")
    
    # 5. Display final results
    print("\n5. Final Status Summary:")
    print("="*50)
    print(f"Listing: {listing.title}")
    print(f"Owner: {owner.get_full_name() or owner.username}")
    print(f"Guest: {guest.get_full_name() or guest.username}")
    print(f"Booking ID: {booking.id}")
    print(f"Check-in: {booking.check_in_date}")
    print(f"Check-out: {booking.check_out_date}")
    print(f"Total Amount: ETB {booking.total_price}")
    print(f"Payment ID: {payment.id}")
    print(f"Transaction ID: {payment.transaction_id}")
    print(f"Payment Status: {payment.status}")
    print(f"Booking Status: {booking.status}")
    print("="*50)
    
    # 6. Show API endpoints that would be used
    print("\n6. Available API Endpoints:")
    print("="*50)
    print(f"POST /api/bookings/{booking.id}/initiate-payment/ - Initiate payment")
    print(f"POST /api/bookings/{booking.id}/verify-payment/ - Verify payment")
    print(f"GET /api/bookings/{booking.id}/payment-success/ - Payment success callback")
    print(f"GET /api/payments/{payment.id}/ - Get payment details")
    print("GET /api/payments/ - List all payments for user")
    print("="*50)
    
    print("\n✅ Payment integration demo completed successfully!")
    print("\nTo use in production:")
    print("1. Get real Chapa API keys from https://developer.chapa.co/")
    print("2. Update CHAPA_SECRET_KEY in .env file")
    print("3. Configure email settings for notifications")
    print("4. Start Celery worker for background tasks")
    print("5. Set up proper database (MySQL/PostgreSQL)")

if __name__ == '__main__':
    demo_payment_workflow()

