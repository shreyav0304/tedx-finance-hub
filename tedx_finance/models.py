from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

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

