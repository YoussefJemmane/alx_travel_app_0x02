"""
Celery tasks for the listings app.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_payment_confirmation_email(user_email, user_name, listing_title, amount):
    """
    Send payment confirmation email to user
    """
    try:
        subject = 'Payment Confirmation - ALX Travel App'
        message = f"""
Dear {user_name},

Your payment has been successfully processed!

Booking Details:
- Property: {listing_title}
- Amount Paid: ETB {amount}

Thank you for choosing ALX Travel App. We hope you have a wonderful stay!

Best regards,
ALX Travel App Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        
        logger.info(f"Payment confirmation email sent to {user_email}")
        return f"Email sent successfully to {user_email}"
        
    except Exception as e:
        logger.error(f"Failed to send payment confirmation email to {user_email}: {e}")
        raise e

