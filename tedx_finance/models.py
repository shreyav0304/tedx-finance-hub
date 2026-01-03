from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from datetime import timedelta
from django.utils import timezone

class Category(models.Model):
    """User-defined transaction categories."""
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class ManagementFund(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_received = models.DateField()
    history = HistoricalRecords()

    def __str__(self):
        return f"Management Fund of {self.amount}"

class Sponsor(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_received = models.DateField()
    
    # --- UPDATED FIELDS ---
    # The 'proof' field has been replaced with 'agreement' and 'contact_email'
    # to match the fields your SponsorForm is expecting.
    agreement = models.FileField(upload_to='sponsors/', blank=True, null=True)
    contact_email = models.EmailField(max_length=254, blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

class Transaction(models.Model):
    CATEGORY_CHOICES = [
        ('Marketing', 'Marketing'),
        ('Logistics', 'Logistics'),
        ('Speakers', 'Speakers'),
        ('Venue', 'Venue'),
        ('Other', 'Other'),
    ]
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    date = models.DateField()
    proof = models.FileField(upload_to='proofs/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # --- NEW FIELD ---
    # This will track whether the transaction has been approved by a treasurer.
    # It defaults to False, so all new transactions start as 'pending'.
    approved = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.title


class Budget(models.Model):
    """Budget tracking per category with alerts when exceeded."""
    # Link budgets to the dynamic Category model so new/custom categories can have budgets
    # Note: Using ForeignKey with unique=True. Django suggests OneToOneField, but this works fine.
    # Changing it requires complex migration, so keeping as-is for stability.
    category = models.ForeignKey(Category, on_delete=models.CASCADE, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Planned budget amount")
    start_date = models.DateField(help_text="Budget period start")
    end_date = models.DateField(help_text="Budget period end")
    
    def __str__(self):
        return f"{self.category.name} Budget ({self.start_date} to {self.end_date})"
    
    def spent(self):
        """Calculate total approved spending within budget period for this category."""
        from django.db.models import Sum
        spent_val = Transaction.objects.filter(
            # Transactions still store category as a string name
            category=self.category.name,
            approved=True,
            amount__lt=0,
            date__gte=self.start_date,
            date__lte=self.end_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        return abs(spent_val)
    
    def remaining(self):
        return float(self.amount) - self.spent()
    
    def is_exceeded(self):
        return self.spent() > float(self.amount)
    
    def utilization_percent(self):
        if float(self.amount) == 0:
            return 0
        return min(100, (self.spent() / float(self.amount)) * 100)


# ===== NEW MODELS FOR ENHANCED SECURITY & FEATURES =====

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


# ===== NEW MODELS FOR ENHANCED SECURITY & FEATURES =====

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
