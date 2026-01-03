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
            'expiration_hours': 24,
        }
        
        message = render_to_string('tedx_finance/emails/verification_email.html', context)
        send_mail(
            subject='Verify your TEDx Finance Hub email',
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@tedxfinancehub.com',
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False,
        )
        logger.info(f"Verification email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False


def send_password_reset_email(user, reset_url):
    """Send password reset email to user."""
    try:
        context = {
            'user': user,
            'reset_url': reset_url,
            'expiration_hours': 24,
        }
        
        message = render_to_string('tedx_finance/emails/password_reset.html', context)
        send_mail(
            subject='Reset your TEDx Finance Hub password',
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@tedxfinancehub.com',
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False,
        )
        logger.info(f"Password reset email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False


def send_login_notification_email(user, request):
    """Send login notification email to user with login details."""
    try:
        ip_address = get_client_ip(request)
        user_agent_string = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        # Simple browser extraction
        browser = 'Unknown'
        if 'Chrome' in user_agent_string:
            browser = 'Chrome'
        elif 'Firefox' in user_agent_string:
            browser = 'Firefox'
        elif 'Safari' in user_agent_string:
            browser = 'Safari'
        elif 'Edge' in user_agent_string:
            browser = 'Edge'
        elif 'Mobile' in user_agent_string:
            browser = 'Mobile Browser'
        
        context = {
            'user': user,
            'login_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'ip_address': ip_address,
            'browser': browser,
            'location': 'Unknown',
        }
        
        message = render_to_string('tedx_finance/emails/login_notification.html', context)
        send_mail(
            subject='New Login to Your TEDx Finance Hub Account',
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@tedxfinancehub.com',
            recipient_list=[user.email],
            html_message=message,
            fail_silently=True,  # Don't fail login if email fails
        )
        logger.info(f"Login notification email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send login notification email to {user.email}: {str(e)}")
        return False


def get_client_ip(request):
    """Extract client IP address from request, handling proxy headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_audit_action(user, action, object_type, object_id, description, ip_address=None):
    """Log an audit action for security and accountability."""
    from .models import AuditLog
    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            object_type=object_type,
            object_id=object_id,
            description=description,
            ip_address=ip_address,
        )
        logger.info(f"Audit logged: {user.username} - {action} on {object_type} {object_id}")
    except Exception as e:
        logger.error(f"Failed to log audit action: {str(e)}")


def create_notification(user, notification_type, title, message, related_object_type=None, related_object_id=None):
    """Create a notification for a user."""
    from .models import Notification
    try:
        Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            related_object_type=related_object_type,
            related_object_id=related_object_id,
        )
        logger.info(f"Notification created for {user.username}: {title}")
    except Exception as e:
        logger.error(f"Failed to create notification: {str(e)}")
