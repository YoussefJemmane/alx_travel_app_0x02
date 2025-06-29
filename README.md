# ALX Travel App - Chapa Payment Integration

A Django-based REST API for a travel booking platform where users can list properties, make bookings, process secure payments, and leave reviews.

## Project Overview

The ALX Travel App is a backend service for a travel booking platform built with Django and Django REST Framework. It provides:

- Property listing management
- Booking functionality with different statuses
- **Secure Payment Processing**: Integration with Chapa API for ETB payments
- **Payment Status Tracking**: Real-time payment status updates (Pending, Completed, Failed)
- **Email Notifications**: Automated confirmation emails sent via Celery background tasks
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

### Payment Model

The `Payment` model represents payment transactions for bookings:

- **Fields**:
  - `booking`: ForeignKey to Booking model
  - `reference`: UUID field for unique payment identification
  - `transaction_id`: Chapa transaction ID
  - `amount`: Payment amount
  - `status`: Payment status (PENDING, COMPLETED, FAILED)
  - `created_at`, `updated_at`: Timestamps

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
- `PaymentSerializer`: Manages payment data with booking relationships
- `ReviewSerializer`: Manages listing reviews with validation for preventing duplicate reviews
- `BookingSerializer`: Handles booking operations with validation for dates, availability, and capacity (includes payments)
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
   
   # Chapa Payment Configuration
   CHAPA_SECRET_KEY=CHASECK_TEST-your-secret-key-here
   CHAPA_PUBLIC_KEY=CHAPUBK_TEST-your-public-key-here
   
   # Email Configuration
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=noreply@alxtravelapp.com
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

8. Set up Chapa Account:
   - Visit [Chapa Developer Portal](https://developer.chapa.co/)
   - Create an account and get your API keys
   - Add keys to your `.env` file

9. Start Celery worker (for email notifications):
   ```
   celery -A alx_travel_app worker --loglevel=info
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

### Core Endpoints
- `/api/listings/` - List and create listings
- `/api/listings/{id}/` - Retrieve, update and delete listings
- `/api/bookings/` - List and create bookings
- `/api/bookings/{id}/` - Retrieve, update and delete bookings
- `/api/payments/` - List payments for authenticated user
- `/api/payments/{id}/` - Retrieve payment details

### Payment Endpoints
- `/api/bookings/{id}/initiate-payment/` - Initiate payment for a booking
- `/api/bookings/{id}/verify-payment/` - Verify payment status
- `/api/bookings/{id}/payment-success/` - Payment success callback

## Additional Notes

- The application uses Celery for background tasks processing
- API documentation is available through Swagger UI at `/api/docs/`
- The project follows Django REST Framework's best practices for API design
- The seed command creates realistic data with random but sensible values

## License

[MIT License](LICENSE)

## API Documentation

The API is documented using Swagger UI and ReDoc. You can access the documentation at:
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`

### Available Endpoints

#### Listings
- `GET /api/listings/` - List all listings
- `POST /api/listings/` - Create a new listing
- `GET /api/listings/{id}/` - Retrieve a specific listing
- `PUT /api/listings/{id}/` - Update a specific listing
- `DELETE /api/listings/{id}/` - Delete a specific listing

#### Bookings
- `GET /api/bookings/` - List all bookings (filtered to show only user's bookings)
- `POST /api/bookings/` - Create a new booking
- `GET /api/bookings/{id}/` - Retrieve a specific booking
- `PUT /api/bookings/{id}/` - Update a specific booking
- `DELETE /api/bookings/{id}/` - Delete a specific booking
- `POST /api/bookings/{id}/initiate-payment/` - Initiate payment for booking
- `POST /api/bookings/{id}/verify-payment/` - Verify payment status
- `GET /api/bookings/{id}/payment-success/` - Payment success redirect

#### Payments
- `GET /api/payments/` - List all payments for authenticated user
- `GET /api/payments/{id}/` - Retrieve specific payment details

## Payment Integration

### Chapa Payment Flow

1. **Create Booking**: User creates a booking (status: PENDING)
2. **Initiate Payment**: Call `/api/bookings/{id}/initiate-payment/`
3. **User Payment**: User completes payment on Chapa checkout page
4. **Verify Payment**: System verifies payment with Chapa API
5. **Confirmation**: Email notification sent to user

### Testing Payments

Use Chapa sandbox environment with test cards:
- **Success**: 4000000000000002
- **Failure**: 4000000000000069
- **CVV**: Any 3 digits
- **Expiry**: Any future date

### Authentication
All endpoints require authentication except for listing retrieval. Use token authentication by including the token in the Authorization header:
```
Authorization: Token your-token-here
```
