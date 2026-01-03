"""
Middleware and decorators for audit logging and security features.
"""
import logging
from functools import wraps
from django.utils.decorators import decorator_from_middleware
from django.utils.deprecation import MiddlewareMixin
from .models import AuditLog
from .utils import get_client_ip

logger = logging.getLogger(__name__)


class AuditLoggingMiddleware(MiddlewareMixin):
    """Middleware to track admin actions for security audit trail."""
    
    def process_request(self, request):
        # Store IP address in request for later use
        request.client_ip = get_client_ip(request)
        return None


def audit_action(action_type, get_object_id=None, get_object_type=None):
    """
    Decorator to log admin actions.
    
    Args:
        action_type: Type of action (e.g., 'approve_transaction', 'delete_fund')
        get_object_id: Callable that extracts object ID from request/args
        get_object_type: Callable that extracts object type from request/args
    
    Example:
        @audit_action('approve_transaction', get_object_id=lambda r: r.POST.get('transaction_id'))
        def approve_transaction(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            
            # Log the action if user is authenticated
            if request.user.is_authenticated:
                try:
                    object_id = get_object_id(request, *args, **kwargs) if get_object_id else kwargs.get('pk')
                    object_type = get_object_type(request, *args, **kwargs) if get_object_type else None
                    ip_address = getattr(request, 'client_ip', get_client_ip(request))
                    
                    AuditLog.objects.create(
                        user=request.user,
                        action=action_type,
                        object_type=object_type or 'Unknown',
                        object_id=object_id or 0,
                        description=f"{request.user.username} performed {action_type}",
                        ip_address=ip_address,
                    )
                except Exception as e:
                    logger.error(f"Failed to log audit action: {str(e)}")
            
            return response
        return wrapper
    return decorator


def log_model_change(sender, instance, created, **kwargs):
    """
    Signal handler to log model creation/updates.
    Connect this to post_save signals on models you want to audit.
    """
    from django.contrib.auth.models import AnonymousUser
    
    try:
        # Get current user from thread-local storage if available
        # This is a fallback for when we can't get user from request
        request = getattr(instance, '_current_request', None)
        user = request.user if request else AnonymousUser()
        
        if user.is_authenticated:
            action = 'create' if created else 'update'
            AuditLog.objects.create(
                user=user,
                action=action,
                object_type=instance.__class__.__name__,
                object_id=instance.id,
                description=f"{action.capitalize()} {instance.__class__.__name__}: {str(instance)[:100]}",
            )
    except Exception as e:
        logger.error(f"Failed to log model change: {str(e)}")
