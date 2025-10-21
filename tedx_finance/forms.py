import os
from datetime import date
from django import forms
from django.core.exceptions import ValidationError
from .models import Transaction, ManagementFund, Sponsor, Category

# --------------------------------------------------
# Reusable Helper Functions for File Validation
# --------------------------------------------------
MAX_UPLOAD_MB = 5  # Set the max file size in megabytes

def validate_file_size(file):
    """
    Validates that the uploaded file does not exceed the maximum allowed size.
    
    Args:
        file: The uploaded file object
        
    Raises:
        ValidationError: If file size exceeds MAX_UPLOAD_MB
    """
    if file and file.size > MAX_UPLOAD_MB * 1024 * 1024:
        raise ValidationError(
            f"File size ({file.size / (1024 * 1024):.2f} MB) exceeds the maximum allowed size of {MAX_UPLOAD_MB} MB."
        )

def validate_file_extension(file):
    """
    Validates that the uploaded file has an allowed extension.
    
    Args:
        file: The uploaded file object
        
    Raises:
        ValidationError: If file extension is not in allowed list
    """
    if file:
        ext = os.path.splitext(file.name)[1].lower()
        allowed = (".jpg", ".jpeg", ".png", ".gif", ".pdf")
        if ext not in allowed:
            raise ValidationError(
                f"File type '{ext}' is not supported. Please upload images (JPG, PNG, GIF) or PDF files only."
            )

# --------------------------------------------------
# Main Transaction Form (for expenses)
# --------------------------------------------------
class TransactionForm(forms.ModelForm):
    """
    Comprehensive form for creating and updating financial transactions.
    
    Features:
    - Staff-only approval checkbox
    - File upload validation (size and type)
    - Amount validation (ensures expenses are negative)
    - Custom styling with Tailwind CSS classes
    """
    approve_now = forms.BooleanField(
        required=False,
        label="Approve immediately",
        help_text="⚡ Staff only: Check this box to approve the transaction immediately.",
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded border-gray-300 text-purple-600 focus:ring-purple-500'
        })
    )

    class Meta:
        model = Transaction
        fields = ["title", "amount", "category", "date", "proof"]
        labels = {
            'title': 'Transaction Title',
            'amount': 'Amount (negative for expenses)',
            'category': 'Expense Category',
            'date': 'Transaction Date',
            'proof': 'Upload Receipt/Proof',
        }
        help_texts = {
            'title': 'Brief description of the expense (e.g., "Venue deposit")',
            'amount': 'Enter negative values for expenses (e.g., -500 for $500 spent)',
            'category': 'Select the budget category this expense belongs to',
            'date': 'When did this expense occur?',
            'proof': f'Upload receipt or proof (Max {MAX_UPLOAD_MB}MB, JPG/PNG/PDF)',
        }
        widgets = {
            "title": forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition',
                'placeholder': 'e.g., Speaker travel expenses'
            }),
            "amount": forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition',
                'placeholder': '-500.00',
                'step': '0.01'
            }),
            "category": forms.Select(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition'
            }),
            "date": forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition'
            }),
            "proof": forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition',
                'accept': 'image/*,.pdf'
            }),
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        # Dynamic category choices: user-defined categories first, then defaults (without duplicates)
        try:
            dynamic = list(Category.objects.all().values_list('name', 'name'))
        except Exception:
            dynamic = []
        default_choices = list(getattr(Transaction, 'CATEGORY_CHOICES', []))
        # Remove duplicates preserving order
        seen = set()
        merged = []
        for val, label in dynamic + default_choices:
            if val not in seen:
                merged.append((val, label))
                seen.add(val)
        if merged:
            self.fields['category'].choices = merged
        # Only show the 'approve_now' checkbox to staff members
        if not self.user or not self.user.is_staff:
            del self.fields['approve_now']

    def clean_title(self):
        """Validate that title is not empty and has reasonable length."""
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise ValidationError("Transaction title cannot be empty.")
        if len(title) < 3:
            raise ValidationError("Transaction title must be at least 3 characters long.")
        return title

    def clean_amount(self):
        """Validate that amount is not zero and expenses are negative."""
        amount = self.cleaned_data.get("amount")
        if amount is None:
            raise ValidationError("Amount is required.")
        if amount == 0:
            raise ValidationError("Amount cannot be zero. Please enter a valid transaction amount.")
        # Ensure expenses are negative (except for sponsor income)
        if self.cleaned_data.get('category') != 'SPONSOR' and amount > 0:
            raise ValidationError(
                "Expenses must be entered as negative numbers. "
                f"Did you mean -{amount}?"
            )
        return amount

    def clean_date(self):
        """Validate that date is not in the future."""
        transaction_date = self.cleaned_data.get("date")
        if transaction_date and transaction_date > date.today():
            raise ValidationError(
                "Transaction date cannot be in the future. "
                "Please enter the actual date of the expense."
            )
        return transaction_date

    def clean_proof(self):
        """Validate uploaded proof file for size and type."""
        proof_file = self.cleaned_data.get("proof", False)
        if proof_file:
            validate_file_size(proof_file)
            validate_file_extension(proof_file)
        return proof_file

    def save(self, commit=True):
        """
        Save the transaction with optional immediate approval.
        
        If the user is staff and 'approve_now' is checked, the transaction
        will be marked as approved immediately.
        """
        transaction = super().save(commit=False)
        # Handle the staff-only approval checkbox
        if self.user and self.user.is_staff and self.cleaned_data.get("approve_now"):
            transaction.approved = True
        if commit:
            transaction.save()
        return transaction

# --------------------------------------------------
# Form for the Initial Management Fund
# --------------------------------------------------
class ManagementFundForm(forms.ModelForm):
    """
    Form to record the initial fund allocation from management.
    
    This represents the starting budget provided by the organization
    before any sponsorships or expenses.
    """
    class Meta:
        model = ManagementFund
        fields = ['amount', 'date_received']
        labels = {
            'amount': 'Initial Fund Amount',
            'date_received': 'Date Received',
        }
        help_texts = {
            'amount': 'Enter the total initial budget provided by management (e.g., 10000)',
            'date_received': 'When was this fund allocation received?',
        }
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition',
                'placeholder': '10000.00',
                'step': '0.01',
                'min': '0'
            }),
            'date_received': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition'
            }),
        }

    def clean_amount(self):
        """Validate that the fund amount is positive."""
        amount = self.cleaned_data.get("amount")
        if amount is None:
            raise ValidationError("Fund amount is required.")
        if amount <= 0:
            raise ValidationError("Initial fund amount must be greater than zero.")
        if amount > 1000000:  # Sanity check for extremely large values
            raise ValidationError(
                "Fund amount seems unusually large. Please verify and enter a reasonable value."
            )
        return amount

    def clean_date_received(self):
        """Validate that date received is not in the future."""
        date_received = self.cleaned_data.get("date_received")
        if date_received and date_received > date.today():
            raise ValidationError(
                "Date received cannot be in the future. Please enter the actual date."
            )
        return date_received

# --------------------------------------------------
# Form for Adding New Sponsors
# --------------------------------------------------
class SponsorForm(forms.ModelForm):
    """
    Form to record new sponsor contributions and agreements.
    
    Features:
    - Email validation for sponsor contacts
    - File upload for sponsorship agreements
    - Amount validation with reasonable limits
    """
    class Meta:
        model = Sponsor
        fields = ['name', 'amount', 'date_received', 'contact_email', 'agreement']
        labels = {
            'name': 'Sponsor Name',
            'amount': 'Sponsorship Amount',
            'date_received': 'Date Received',
            'contact_email': 'Contact Email',
            'agreement': 'Upload Agreement',
        }
        help_texts = {
            'name': 'Full name or company name of the sponsor',
            'amount': 'Total sponsorship amount received (e.g., 5000)',
            'date_received': 'When was the sponsorship received?',
            'contact_email': 'Primary contact email for this sponsor',
            'agreement': f'Upload signed sponsorship agreement (Max {MAX_UPLOAD_MB}MB, JPG/PNG/PDF)',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition',
                'placeholder': 'e.g., Tech Corp Inc.'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition',
                'placeholder': '5000.00',
                'step': '0.01',
                'min': '0'
            }),
            'date_received': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition',
                'placeholder': 'sponsor@example.com'
            }),
            'agreement': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition',
                'accept': 'image/*,.pdf'
            }),
        }

    def clean_name(self):
        """Validate sponsor name."""
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise ValidationError("Sponsor name is required.")
        if len(name) < 2:
            raise ValidationError("Sponsor name must be at least 2 characters long.")
        return name

    def clean_amount(self):
        """Validate that sponsorship amount is positive and reasonable."""
        amount = self.cleaned_data.get("amount")
        if amount is None:
            raise ValidationError("Sponsorship amount is required.")
        if amount <= 0:
            raise ValidationError("Sponsorship amount must be greater than zero.")
        if amount > 1000000:  # Sanity check
            raise ValidationError(
                "Sponsorship amount seems unusually large. Please verify and enter a reasonable value."
            )
        return amount

    def clean_date_received(self):
        """Validate that date received is not in the future."""
        date_received = self.cleaned_data.get("date_received")
        if date_received and date_received > date.today():
            raise ValidationError(
                "Date received cannot be in the future. Please enter the actual date."
            )
        return date_received

    def clean_contact_email(self):
        """Validate and normalize email address."""
        email = self.cleaned_data.get("contact_email", "").strip().lower()
        if email and '@' not in email:
            raise ValidationError("Please enter a valid email address.")
        return email

    def clean_agreement(self):
        """Validate uploaded agreement file for size and type."""
        agreement_file = self.cleaned_data.get("agreement", False)
        if agreement_file:
            validate_file_size(agreement_file)
            validate_file_extension(agreement_file)
        return agreement_file

