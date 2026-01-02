# Additional models for new features

from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone


class AuditLog(models.Model):
    """Track all admin actions for security and accountability."""
    ACTION_CHOICES = [
        ('approve_transaction', 'Approved Transaction'),
        ('reject_transaction', 'Rejected Transaction'),
        ('delete_transaction', 'Deleted Transaction'),
        ('create_fund', 'Created Fund'),
        ('update_fund', 'Updated Fund'),
        ('delete_fund', 'Deleted Fund'),
        ('create_category', 'Created Category'),
        ('update_category', 'Updated Category'),
        ('delete_category', 'Deleted Category'),
        ('export_data', 'Exported Data'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    object_type = models.CharField(max_length=50)  # e.g., 'Transaction', 'Fund'
    object_id = models.IntegerField()
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} on {self.timestamp}"


class LoginAttempt(models.Model):
    """Track login attempts for rate limiting and security."""
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['ip_address', '-timestamp']),
            models.Index(fields=['username', '-timestamp']),
        ]
    
    @classmethod
    def is_rate_limited(cls, ip_address, max_attempts=5, time_window=300):
        """Check if an IP has exceeded login attempts in the time window (seconds)."""
        cutoff_time = timezone.now() - timedelta(seconds=time_window)
        recent_attempts = cls.objects.filter(
            ip_address=ip_address,
            timestamp__gte=cutoff_time
        )
        failed_attempts = recent_attempts.filter(success=False).count()
        return failed_attempts >= max_attempts
    
    @classmethod
    def log_attempt(cls, username, ip_address, success):
        """Log a login attempt."""
        cls.objects.create(
            username=username,
            ip_address=ip_address,
            success=success
        )


class EmailVerification(models.Model):
    """Track email verification status for new users."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    token = models.CharField(max_length=255, unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    def is_token_valid(self, hours=24):
        """Check if token is still valid (not expired)."""
        expiration_time = self.created_at + timedelta(hours=hours)
        return timezone.now() < expiration_time
    
    def __str__(self):
        return f"{self.user.username} - {'Verified' if self.is_verified else 'Pending'}"


class Notification(models.Model):
    """User notifications for system events."""
    NOTIFICATION_TYPES = [
        ('transaction_approved', 'Transaction Approved'),
        ('transaction_rejected', 'Transaction Rejected'),
        ('fund_created', 'Fund Created'),
        ('fund_low', 'Fund Running Low'),
        ('budget_exceeded', 'Budget Exceeded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_object_type = models.CharField(max_length=50, null=True, blank=True)
    related_object_id = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
