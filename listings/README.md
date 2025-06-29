# ALX Travel App

A Django-based REST API for a travel booking platform where users can list properties, make bookings, and leave reviews.

## Project Overview

The ALX Travel App is a backend service for a travel booking platform built with Django and Django REST Framework. It provides:

- Property listing management
- Booking functionality with different statuses
- Review system for listings
- RESTful API endpoints for all functionality
- Database models with proper relationships and validations
- Serializers for API data representation
- Data seeding command for generating sample data

## Database Models

### Listing Model

The `Listing` model represents a property that can be booked:

- **Fields**:
  - `owner`: ForeignKey to User model (the property owner)
  - `title`: Property title
  - `description`: Detailed description of the property
  - `price`: Per night price
  - `location`: Geographic location
  - `capacity`: Maximum number of guests
  - `amenities`: List of available amenities
  - `availability_start`, `availability_end`: Date range when the property is available
  - `is_available`: Boolean indicating if the property is currently available for booking
  - `created_at`, `updated_at`: Timestamps

### Booking Model

The `Booking` model represents a reservation for a listing:

- **Fields**:
  - `listing`: ForeignKey to Listing model
  - `guest`: ForeignKey to User model (the person booking)
  - `check_in_date`, `check_out_date`: Stay duration
  - `guests_count`: Number of guests
  - `total_price`: Total calculated price
  - `status`: Current status (PENDING, CONFIRMED, CANCELLED, COMPLETED)
  - `created_at`, `updated_at`: Timestamps
  
- **Methods**:
  - Automatically calculates the total price based on the listing price and stay duration

### Review Model

The `Review` model represents a guest's review of a listing:

- **Fields**:
  - `listing`: ForeignKey to Listing model
  - `author`: ForeignKey to User model
  - `rating`: Numerical rating (1-5)
  - `comment`: Text review
  - `created_at`: Timestamp
  
- **Constraints**:
  - A user can only leave one review per listing

## Serializers

The project includes the following serializers:

- `UserSerializer`: Represents User model data (for nested representations)
- `ReviewSerializer`: Manages listing reviews with validation for preventing duplicate reviews
- `BookingSerializer`: Handles booking operations with validation for dates, availability, and capacity
- `ListingSerializer`: Comprehensive listing representation including nested reviews and bookings
- `ListingListSerializer`: Simplified listing representation for list views with aggregated review data

## Setup Instructions

### Prerequisites

- Python 3.8+
- MySQL
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/alx_travel_app_0x00.git
   cd alx_travel_app_0x00
   ```

2. Create and activate a virtual environment:
   ```
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following content:
   ```
   DEBUG=True
   SECRET_KEY="your_secret_key_here"
   DB_NAME=alx_travel_db
   DB_USER=your_db_username
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=3306
   ```

5. Create the MySQL database:
   ```
   mysql -u your_db_username -p
   CREATE DATABASE alx_travel_db;
   EXIT;
   ```

6. Run migrations:
   ```
   python manage.py migrate
   ```

7. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

## Using the Seed Command

The project includes a management command to populate the database with sample data. You can use it to quickly create users, listings, bookings, and reviews for testing and development.

### Basic Usage

```
python manage.py seed
```

This will create:
- 10 users
- 20 listings
- 30 bookings
- 40 reviews (if possible)

### Custom Options

You can customize the amount of data created:

```
python manage.py seed --users 5 --listings 10 --bookings 15 --reviews 20
```

To clear existing data before seeding:

```
python manage.py seed --clear
```

## Running the Project

1. Start the development server:
   ```
   python manage.py runserver
   ```

2. Access the admin interface at `http://127.0.0.1:8000/admin/`

3. Access the API endpoints at `http://127.0.0.1:8000/api/`

## API Endpoints

- `/api/listings/` - List and create listings
- `/api/listings/{id}/` - Retrieve, update and delete listings
- `/api/bookings/` - List and create bookings
- `/api/bookings/{id}/` - Retrieve, update and delete bookings
- `/api/reviews/` - List and create reviews
- `/api/reviews/{id}/` - Retrieve, update and delete reviews

## Additional Notes

- The application uses Celery for background tasks processing
- API documentation is available through Swagger UI at `/api/docs/`
- The project follows Django REST Framework's best practices for API design
- The seed command creates realistic data with random but sensible values

## License

[MIT License](LICENSE)
