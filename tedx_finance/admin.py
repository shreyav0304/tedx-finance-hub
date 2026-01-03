from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    ManagementFund, Sponsor, Transaction, Budget, Category,
    AuditLog, LoginAttempt, EmailVerification, Notification
)

@admin.register(ManagementFund)
class ManagementFundAdmin(SimpleHistoryAdmin):
    # FIX: Changed 'initial_amount' to 'amount' to match the model
    list_display = ('amount', 'date_received')
    search_fields = ('amount',)

@admin.register(Sponsor)
class SponsorAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'amount', 'date_received')
    search_fields = ('name',)
    list_filter = ('date_received',)

@admin.register(Transaction)
class TransactionAdmin(SimpleHistoryAdmin):
    list_display = ('title', 'amount', 'category', 'date', 'created_by', 'approved')
    # FIX: Changed 'user' to 'created_by' to match the model
    list_filter = ('category', 'approved', 'created_by')
    search_fields = ('title', 'created_by__username')
    actions = ['approve_transactions']

    def approve_transactions(self, request, queryset):
        queryset.update(approved=True)
    approve_transactions.short_description = "Mark selected transactions as approved"


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('category', 'amount', 'start_date', 'end_date', 'spent', 'remaining')
    list_filter = ('category',)
    
    def spent(self, obj):
        return f"₹{obj.spent():.2f}"
    
    def remaining(self, obj):
        rem = obj.remaining()
        return f"₹{rem:.2f}" if rem >= 0 else f"-₹{abs(rem):.2f}"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


# ===== NEW ADMIN PANELS FOR SECURITY & FEATURES =====

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'object_type', 'ip_address')
    list_filter = ('action', 'timestamp', 'user')
    search_fields = ('user__username', 'description', 'ip_address')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp', 'user', 'action', 'object_type', 'description', 'ip_address')
    
    def has_add_permission(self, request):
        """Audit logs should not be manually added."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Audit logs should not be deleted."""
        return False


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'username', 'ip_address', 'success')
    list_filter = ('success', 'timestamp')
    search_fields = ('username', 'ip_address')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp', 'username', 'ip_address', 'success')
    
    def has_add_permission(self, request):
        """Login attempts should not be manually added."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Login attempts should not be deleted."""
        return False


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'created_at', 'verified_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('token', 'created_at', 'verified_at')
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Verification Status', {'fields': ('is_verified', 'token')}),
        ('Timestamps', {'fields': ('created_at', 'verified_at')}),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at', 'user')
    search_fields = ('user__username', 'title', 'message')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('User & Notification', {'fields': ('user', 'notification_type')}),
        ('Content', {'fields': ('title', 'message')}),
        ('Status', {'fields': ('is_read',)}),
        ('Related Object', {'fields': ('related_object_type', 'related_object_id')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )

