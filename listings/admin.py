from django.contrib import admin
from .models import Listing, Booking, Review, Payment


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'price', 'location', 'capacity', 'is_available', 'created_at']
    list_filter = ['is_available', 'created_at', 'location']
    search_fields = ['title', 'location', 'owner__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating a new object
            obj.owner = request.user
        super().save_model(request, obj, form, change)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['listing', 'guest', 'check_in_date', 'check_out_date', 
                   'guests_count', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'check_in_date']
    search_fields = ['listing__title', 'guest__username']
    readonly_fields = ['created_at', 'updated_at', 'total_price']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['listing', 'guest']
        return self.readonly_fields


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'booking', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['transaction_id', 'booking__guest__username', 'booking__listing__title']
    readonly_fields = ['reference', 'created_at', 'updated_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['booking', 'transaction_id']
        return self.readonly_fields


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['listing', 'author', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['listing__title', 'author__username']
    readonly_fields = ['created_at']
