from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import ManagementFund, Sponsor, Transaction, Budget, Category

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

