"""
Models for the listings app.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
import uuid


class Listing(models.Model):
    """
    Model for travel listings
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(default=1)
    amenities = models.TextField(blank=True)
    availability_start = models.DateField(null=True, blank=True)
    availability_end = models.DateField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title


class Booking(models.Model):
    """
    Model for booking listings
    """
    class BookingStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        CANCELLED = 'CANCELLED', _('Cancelled')
        COMPLETED = 'COMPLETED', _('Completed')
    
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    guests_count = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.guest.username}'s booking for {self.listing.title}"
    
    def save(self, *args, **kwargs):
        # Calculate total price if not provided
        if not self.total_price:
            # Calculate number of days
            days = (self.check_out_date - self.check_in_date).days
            if days < 1:
                days = 1
            self.total_price = self.listing.price * days
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    Model for handling payment information
    """
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"

class Review(models.Model):
    """
    Model for listing reviews
    """
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('listing', 'author')
    
    def __str__(self):
        return f"Review by {self.author.username} for {self.listing.title}"
