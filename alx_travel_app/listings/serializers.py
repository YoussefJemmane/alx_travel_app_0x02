"""
Serializers for the listings app.
"""
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Listing, Booking, Review


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model (used for nested representations)
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model
    """
    author = UserSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='author'
    )

    class Meta:
        model = Review
        fields = [
            'id', 'listing', 'author', 'author_id', 'rating', 
            'comment', 'created_at'
        ]
        read_only_fields = ['created_at']

    def validate(self, data):
        """
        Validate that a user can only leave one review per listing
        """
        # Skip validation when updating an existing review
        if self.instance:
            return data
            
        # For new reviews, check if the user already reviewed this listing
        listing = data.get('listing')
        author = data.get('author')
        
        if Review.objects.filter(listing=listing, author=author).exists():
            raise serializers.ValidationError(
                "You have already reviewed this listing"
            )
        
        return data


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Booking model
    """
    guest = UserSerializer(read_only=True)
    guest_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='guest'
    )
    listing_title = serializers.ReadOnlyField(source='listing.title')
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_title', 'guest', 'guest_id',
            'check_in_date', 'check_out_date', 'guests_count',
            'total_price', 'status', 'status_display', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'total_price']

    def validate(self, data):
        """
        Validate booking dates and capacity
        """
        check_in_date = data.get('check_in_date')
        check_out_date = data.get('check_out_date')
        guests_count = data.get('guests_count')
        listing = data.get('listing')
        
        # Validate check-in date is not in the past
        today = timezone.now().date()
        if check_in_date and check_in_date < today:
            raise serializers.ValidationError(
                {"check_in_date": "Check-in date cannot be in the past"}
            )
            
        # Validate check-out date is after check-in date
        if check_in_date and check_out_date and check_out_date <= check_in_date:
            raise serializers.ValidationError(
                {"check_out_date": "Check-out date must be after check-in date"}
            )
            
        # Validate listing is available for the selected dates
        if listing and check_in_date and check_out_date:
            if not listing.is_available:
                raise serializers.ValidationError(
                    "This listing is not available for booking"
                )
                
            if listing.availability_start and check_in_date < listing.availability_start:
                raise serializers.ValidationError(
                    {"check_in_date": f"Listing is only available from {listing.availability_start}"}
                )
                
            if listing.availability_end and check_out_date > listing.availability_end:
                raise serializers.ValidationError(
                    {"check_out_date": f"Listing is only available until {listing.availability_end}"}
                )
                
            # Check for overlapping bookings
            overlapping_bookings = Booking.objects.filter(
                listing=listing,
                status__in=['PENDING', 'CONFIRMED'],
                check_in_date__lt=check_out_date,
                check_out_date__gt=check_in_date
            )
            
            # Exclude current booking when updating
            if self.instance:
                overlapping_bookings = overlapping_bookings.exclude(pk=self.instance.pk)
                
            if overlapping_bookings.exists():
                raise serializers.ValidationError(
                    "The listing is already booked for the selected dates"
                )
                
        # Validate guests count against listing capacity
        if listing and guests_count and guests_count > listing.capacity:
            raise serializers.ValidationError(
                {"guests_count": f"Maximum capacity for this listing is {listing.capacity} guests"}
            )
            
        return data


class ListingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Listing model
    """
    owner = UserSerializer(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='owner'
    )
    reviews = ReviewSerializer(many=True, read_only=True)
    bookings = BookingSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'id', 'owner', 'owner_id', 'title', 'description', 
            'price', 'location', 'capacity', 'amenities',
            'availability_start', 'availability_end', 'is_available',
            'created_at', 'updated_at', 'reviews', 'bookings',
            'average_rating'
        ]
        read_only_fields = ['created_at', 'updated_at']
        
    def get_average_rating(self, obj):
        """
        Calculate the average rating for a listing
        """
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return sum(review.rating for review in reviews) / reviews.count()
        
    def validate(self, data):
        """
        Validate availability dates
        """
        availability_start = data.get('availability_start')
        availability_end = data.get('availability_end')
        
        if availability_start and availability_end and availability_end < availability_start:
            raise serializers.ValidationError(
                {"availability_end": "End date must be after start date"}
            )
            
        return data


class ListingListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing list views
    """
    owner = UserSerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'id', 'owner', 'title', 'price', 'location', 
            'capacity', 'is_available', 'average_rating', 'reviews_count'
        ]
        
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return sum(review.rating for review in reviews) / reviews.count()
        
    def get_reviews_count(self, obj):
        return obj.reviews.count()

