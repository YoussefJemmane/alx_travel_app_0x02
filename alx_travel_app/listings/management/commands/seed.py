"""
Management command to seed the database with sample data.
"""
import random
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from faker import Faker
from listings.models import Listing, Booking, Review


class Command(BaseCommand):
    """
    Command to seed database with sample data
    """
    help = 'Seeds the database with sample data for listings, bookings, and reviews'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create'
        )
        parser.add_argument(
            '--listings',
            type=int,
            default=20,
            help='Number of listings to create'
        )
        parser.add_argument(
            '--bookings',
            type=int,
            default=30,
            help='Number of bookings to create'
        )
        parser.add_argument(
            '--reviews',
            type=int,
            default=40,
            help='Number of reviews to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        """
        Handle the command execution
        """
        fake = Faker()
        user_count = options['users']
        listing_count = options['listings']
        booking_count = options['bookings']
        review_count = options['reviews']
        clear_data = options['clear']

        self.stdout.write(
            self.style.SUCCESS(f'Starting to seed database...')
        )

        # Clear existing data if requested
        if clear_data:
            self.clear_data()

        with transaction.atomic():
            # Create users
            users = self.create_users(user_count, fake)
            self.stdout.write(
                self.style.SUCCESS(f'Created {len(users)} users')
            )

            # Create listings
            listings = self.create_listings(listing_count, users, fake)
            self.stdout.write(
                self.style.SUCCESS(f'Created {len(listings)} listings')
            )

            # Create bookings
            bookings = self.create_bookings(booking_count, listings, users, fake)
            self.stdout.write(
                self.style.SUCCESS(f'Created {len(bookings)} bookings')
            )

            # Create reviews
            reviews = self.create_reviews(review_count, listings, users, fake)
            self.stdout.write(
                self.style.SUCCESS(f'Created {len(reviews)} reviews')
            )

        self.stdout.write(
            self.style.SUCCESS('Database seeding completed successfully!')
        )

    def clear_data(self):
        """
        Clear existing data
        """
        self.stdout.write('Clearing existing data...')
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()
        # We're not deleting users to preserve any admin users
        self.stdout.write(self.style.SUCCESS('Data cleared successfully!'))

    def create_users(self, count, fake):
        """
        Create sample users
        """
        users = []
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            users.append(admin)
            self.stdout.write('Created superuser: admin')

        # Create regular users
        for i in range(count):
            username = fake.user_name() + str(random.randint(1, 9999))
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = fake.email()
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=first_name,
                last_name=last_name
            )
            users.append(user)
            
        return users

    def create_listings(self, count, users, fake):
        """
        Create sample listings
        """
        listings = []
        locations = [
            'New York, USA', 'Paris, France', 'London, UK', 'Tokyo, Japan',
            'Sydney, Australia', 'Barcelona, Spain', 'Rome, Italy', 
            'Amsterdam, Netherlands', 'Berlin, Germany', 'Cairo, Egypt',
            'Cape Town, South Africa', 'Dubai, UAE', 'Hong Kong, China',
            'Singapore', 'San Francisco, USA', 'Rio de Janeiro, Brazil',
            'Mexico City, Mexico', 'Toronto, Canada', 'Moscow, Russia',
            'Istanbul, Turkey'
        ]
        
        amenities_options = [
            'WiFi', 'Air Conditioning', 'Kitchen', 'Washer', 'Dryer', 
            'Free Parking', 'Swimming Pool', 'TV', 'Breakfast', 'Gym',
            'Hot Tub', 'Balcony', 'Ocean View', 'Mountain View', 'Beach Access',
            'Private Entrance', 'Elevator', 'Security System', 'Coffee Maker',
            'Workspace', 'BBQ Grill', 'Fireplace', 'Pets Allowed'
        ]
        
        for i in range(count):
            # Randomly select 3-8 amenities
            num_amenities = random.randint(3, 8)
            selected_amenities = random.sample(amenities_options, num_amenities)
            amenities_str = ', '.join(selected_amenities)
            
            # Random availability period in the future
            today = timezone.now().date()
            avail_start = today + datetime.timedelta(days=random.randint(1, 30))
            avail_end = avail_start + datetime.timedelta(days=random.randint(60, 180))
            
            # Random pricing
            price = round(random.uniform(50, 500), 2)
            
            # Create the listing
            listing = Listing.objects.create(
                owner=random.choice(users),
                title=fake.sentence(nb_words=5)[:-1],  # Remove period from end
                description=fake.paragraph(nb_sentences=5),
                price=price,
                location=random.choice(locations),
                capacity=random.randint(1, 10),
                amenities=amenities_str,
                availability_start=avail_start,
                availability_end=avail_end,
                is_available=random.random() > 0.1  # 90% are available
            )
            listings.append(listing)
            
        return listings

    def create_bookings(self, count, listings, users, fake):
        """
        Create sample bookings
        """
        bookings = []
        status_choices = ['PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED']
        weights = [0.1, 0.6, 0.1, 0.2]  # Make CONFIRMED more likely
        
        for i in range(min(count, len(listings) * 3)):  # Max 3 bookings per listing
            # Get a random available listing
            available_listings = [listing for listing in listings if listing.is_available]
            if not available_listings:
                break
                
            listing = random.choice(available_listings)
            
            # Ensure guest is not the owner
            potential_guests = [user for user in users if user != listing.owner]
            if not potential_guests:
                continue
                
            guest = random.choice(potential_guests)
            
            # Generate random dates within the listing's availability period
            if listing.availability_start and listing.availability_end:
                min_date = listing.availability_start
                max_date = listing.availability_end
                
                check_in_date = min_date + datetime.timedelta(
                    days=random.randint(0, (max_date - min_date).days - 3)
                )
                stay_duration = random.randint(1, 7)
                check_out_date = check_in_date + datetime.timedelta(days=stay_duration)
                
                # Ensure check_out_date doesn't exceed availability_end
                if check_out_date > max_date:
                    check_out_date = max_date
                
                # Random number of guests (not exceeding capacity)
                guests_count = random.randint(1, listing.capacity)
                
                # Calculate total price
                days = (check_out_date - check_in_date).days
                if days < 1:
                    days = 1
                total_price = listing.price * days
                
                # Random status (weighted)
                status = random.choices(
                    status_choices, 
                    weights=weights, 
                    k=1
                )[0]
                
                # Create the booking
                booking = Booking.objects.create(
                    listing=listing,
                    guest=guest,
                    check_in_date=check_in_date,
                    check_out_date=check_out_date,
                    guests_count=guests_count,
                    total_price=total_price,
                    status=status
                )
                bookings.append(booking)
        
        return bookings

    def create_reviews(self, count, listings, users, fake):
        """
        Create sample reviews
        """
        reviews = []
        # Get count but not more than number of listings
        review_count = min(count, len(listings) * 2)  # Max 2 reviews per listing
        
        for i in range(review_count):
            # Get a random listing
            listing = random.choice(listings)
            
            # Ensure author is not the owner
            potential_authors = [user for user in users if user != listing.owner]
            if not potential_authors:
                continue
                
            author = random.choice(potential_authors)
            
            # Check if this user has already reviewed this listing
            if Review.objects.filter(listing=listing, author=author).exists():
                continue
                
            # Random rating and comment
            rating = random.randint(1, 5)
            
            # Make comments more realistic based on rating
            if rating >= 4:
                comment = fake.paragraph(nb_sentences=random.randint(1, 3))
                if rating == 5:
                    comment = "Absolutely loved this place! " + comment
            elif rating == 3:
                comment = "Decent place, but could be better. " + fake.paragraph(nb_sentences=random.randint(1, 2))
            else:
                comment = "Disappointed with this listing. " + fake.paragraph(nb_sentences=random.randint(1, 2))
                
            # Create the review
            review = Review.objects.create(
                listing=listing,
                author=author,
                rating=rating,
                comment=comment
            )
            reviews.append(review)
            
        return reviews

