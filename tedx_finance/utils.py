# Utility functions for new features

import secrets
import logging
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timedelta

logger = logging.getLogger(__name__)


def generate_email_token():
    """Generate a secure token for email verification."""
    return secrets.token_urlsafe(32)


def send_verification_email(user, token, request):
    """Send email verification link to user."""
    try:
        verification_url = request.build_absolute_uri(
            f'/verify-email/{token}/'
        )
        
        context = {
            'user': user,
            'verification_url': verification_url,
            'token': token,
        }
        
        message = render_to_string('emails/verification_email.html', context)
        send_mail(
            subject='Verify your TEDx Finance Hub email',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False,
        )
        logger.info(f"Verification email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False


def log_audit_action(user, action, object_type, object_id, description, ip_address=None):
    """Log an audit action."""
    from .models_improvements import AuditLog
    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            object_type=object_type,
            object_id=object_id,
            description=description,
            ip_address=ip_address,
        )
        logger.debug(f"Audit log created: {user.username} - {action}")
    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}")


def create_notification(user, notification_type, title, message, related_type=None, related_id=None):
    """Create a user notification."""
    from .models_improvements import Notification
    try:
        Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            related_object_type=related_type,
            related_object_id=related_id,
        )
        logger.debug(f"Notification created for {user.username}: {title}")
    except Exception as e:
        logger.error(f"Failed to create notification: {str(e)}")


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def check_rate_limit(request, max_attempts=5, time_window=300):
    """Check if request IP is rate limited."""
    from .models_improvements import LoginAttempt
    ip = get_client_ip(request)
    return LoginAttempt.is_rate_limited(ip, max_attempts, time_window)


def log_login_attempt(request, username, success):
    """Log a login attempt."""
    from .models_improvements import LoginAttempt
    ip = get_client_ip(request)
    LoginAttempt.log_attempt(username, ip, success)
