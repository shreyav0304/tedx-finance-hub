from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth
import logging

from .models import ManagementFund, Sponsor, Transaction, Category
from .forms import TransactionForm, ManagementFundForm, SponsorForm

import openpyxl

# Configure logger
logger = logging.getLogger(__name__)


# --- Helper functions ---
def is_in_group(user, group_name):
    """
    Checks if a user is in a given group.
    Admins (staff users) automatically have access to 'Treasurer' group.
    """
    if user.is_authenticated:
        # Admins get automatic access to Treasurer group
        if group_name == 'Treasurer' and user.is_staff:
            return True
        return user.groups.filter(name=group_name).exists()
    return False


def parse_date(date_str):
    """
    Safely parse a date string in YYYY-MM-DD format.
    Returns a date object or None if parsing fails.
    """
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None
    return None


def get_sponsor_tier(amount):
    """
    Returns sponsor tier name and badge class based on amount.
    Thresholds (INR): Gold ≥ 200,000; Silver ≥ 50,000; Bronze < 50,000
    """
    try:
        amt = float(amount)
    except (ValueError, TypeError):
        amt = 0.0
    
    if amt >= 200000:
        return 'Gold', 'bg-yellow-500 text-black'
    elif amt >= 50000:
        return 'Silver', 'bg-slate-300 text-slate-900'
    else:
        return 'Bronze', 'bg-amber-700 text-white'

# --- Authentication ---
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    context = {'form': form}
    return render(request, 'registration/signup.html', context)

# --- Core Views ---
@login_required
def budgets(request):
    """Budget tracking view showing all budgets and their utilization."""
    from .models import Budget
    user_is_treasurer = is_in_group(request.user, 'Treasurer')
    budgets = Budget.objects.all().order_by('category__name')
    context = {
        'budgets': budgets,
        'is_treasurer': user_is_treasurer,
    }
    return render(request, 'tedx_finance/budgets.html', context)


@login_required
def budget_suggestions(request):
    """
    AI-powered budget prediction and recommendations.
    
    Analyzes:
    - Historical spending patterns
    - Burn rate (spending velocity)
    - Category-wise allocation efficiency
    - Projected budget needs for upcoming period
    - Risk of budget overrun
    """
    from .models import Budget
    from django.db.models import Sum, Count, Avg
    from django.db.models.functions import TruncWeek
    from datetime import datetime, timedelta
    import json
    
    user_is_treasurer = is_in_group(request.user, 'Treasurer')
    
    # Get all budgets and current financial state
    budgets = Budget.objects.all().order_by('category__name')
    
    # Calculate total income
    total_income = (
        (ManagementFund.objects.aggregate(total=Sum('amount'))['total'] or 0) +
        (Sponsor.objects.aggregate(total=Sum('amount'))['total'] or 0)
    )
    
    # Calculate total spent (approved transactions)
    total_spent_val = Transaction.objects.filter(
        approved=True,
        amount__lt=0
    ).aggregate(total=Sum('amount'))['total'] or 0
    total_spent = abs(total_spent_val)
    
    remaining_funds = total_income - total_spent
    
    # Analyze spending patterns (last 30 days)
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_spending = abs(Transaction.objects.filter(
        approved=True,
        amount__lt=0,
        date__gte=thirty_days_ago
    ).aggregate(total=Sum('amount'))['total'] or 0)
    
    # Calculate burn rate (spending per day)
    days_analyzed = min(30, (datetime.now().date() - thirty_days_ago).days)
    if days_analyzed > 0:
        daily_burn_rate = recent_spending / days_analyzed
        weekly_burn_rate = daily_burn_rate * 7
        monthly_burn_rate = daily_burn_rate * 30
    else:
        daily_burn_rate = weekly_burn_rate = monthly_burn_rate = 0
    
    # Calculate runway (days until funds run out at current burn rate)
    if daily_burn_rate > 0:
        runway_days = int(remaining_funds / daily_burn_rate)
    else:
        runway_days = 999  # Infinite if not spending
    
    # Category-wise analysis with predictions
    category_insights = []
    total_suggested_budget = 0
    
    for budget in budgets:
        spent = budget.spent()
        remaining = budget.remaining()
        utilization = budget.utilization_percent()
        
        # Calculate category burn rate (last 30 days)
        category_recent_spending = abs(Transaction.objects.filter(
            category=budget.category.name,
            approved=True,
            amount__lt=0,
            date__gte=thirty_days_ago
        ).aggregate(total=Sum('amount'))['total'] or 0)
        
        if days_analyzed > 0:
            category_daily_burn = category_recent_spending / days_analyzed
        else:
            category_daily_burn = 0
        
        # Calculate days remaining in budget period
        days_remaining = max(0, (budget.end_date - datetime.now().date()).days)
        
        # Predict total spending by end of budget period
        predicted_additional_spend = category_daily_burn * days_remaining
        predicted_total_spend = spent + predicted_additional_spend
        
        # Calculate suggested budget (120% of predicted to have buffer)
        suggested_budget = predicted_total_spend * 1.2
        total_suggested_budget += suggested_budget
        
        # Determine status and risk level
        if utilization >= 100:
            status = 'exceeded'
            risk_level = 'critical'
        elif utilization >= 80:
            status = 'warning'
            risk_level = 'high'
        elif utilization >= 60:
            status = 'moderate'
            risk_level = 'medium'
        else:
            status = 'good'
            risk_level = 'low'
        
        # Calculate if more budget is needed
        budget_shortage = max(0, predicted_total_spend - float(budget.amount))
        
        category_insights.append({
            'category': budget.category.name,
            'category_code': budget.category.name,
            'current_budget': float(budget.amount),
            'spent': spent,
            'remaining': remaining,
            'utilization': round(utilization, 1),
            'daily_burn_rate': round(category_daily_burn, 2),
            'predicted_total_spend': round(predicted_total_spend, 2),
            'suggested_budget': round(suggested_budget, 2),
            'budget_shortage': round(budget_shortage, 2),
            'days_remaining': days_remaining,
            'status': status,
            'risk_level': risk_level,
            'needs_increase': budget_shortage > 0,
        })
    
    # Overall recommendations
    overall_budget_needed = max(total_suggested_budget, total_spent + (monthly_burn_rate * 2))
    additional_funds_needed = max(0, overall_budget_needed - total_income)
    
    # Generate insights and recommendations
    recommendations = []
    
    if runway_days < 30:
        recommendations.append({
            'type': 'critical',
            'icon': '🚨',
            'title': 'Critical: Funds Running Low',
            'message': f'At current spending rate, you have only {runway_days} days of runway. Immediate action required!',
            'action': f'Secure additional ₹{round(monthly_burn_rate * 2):,.0f} to ensure 60 days of operations.'
        })
    elif runway_days < 60:
        recommendations.append({
            'type': 'warning',
            'icon': '⚠️',
            'title': 'Warning: Limited Runway',
            'message': f'You have {runway_days} days of runway remaining.',
            'action': f'Plan to secure ₹{round(monthly_burn_rate):,.0f} within next month.'
        })
    
    for insight in category_insights:
        if insight['needs_increase']:
            recommendations.append({
                'type': 'info',
                'icon': '💡',
                'title': f"{insight['category']} Budget Increase Needed",
                'message': f"Current trend suggests you'll exceed budget by ₹{insight['budget_shortage']:,.0f}",
                'action': f"Consider increasing {insight['category']} budget to ₹{insight['suggested_budget']:,.0f}"
            })
    
    if additional_funds_needed > 0:
        recommendations.append({
            'type': 'info',
            'icon': '💰',
            'title': 'Additional Funding Required',
            'message': f'To complete event safely, you need ₹{round(additional_funds_needed):,.0f} more',
            'action': 'Focus on sponsor acquisition or reduce discretionary spending'
        })
    
    if not recommendations:
        recommendations.append({
            'type': 'success',
            'icon': '✅',
            'title': 'Budget Healthy',
            'message': 'Your budget allocation looks good! All categories are on track.',
            'action': 'Continue monitoring spending patterns regularly.'
        })
    
    # Weekly spending trend (last 8 weeks)
    eight_weeks_ago = datetime.now().date() - timedelta(weeks=8)
    weekly_spending = Transaction.objects.filter(
        approved=True,
        amount__lt=0,
        date__gte=eight_weeks_ago
    ).annotate(
        week=TruncWeek('date')
    ).values('week').annotate(
        total=Sum('amount')
    ).order_by('week')
    
    spending_trend_labels = [item['week'].strftime('%b %d') for item in weekly_spending]
    spending_trend_values = [abs(float(item['total'])) for item in weekly_spending]
    
    context = {
        'is_treasurer': user_is_treasurer,
        'total_income': total_income,
        'total_spent': total_spent,
        'remaining_funds': remaining_funds,
        'daily_burn_rate': round(daily_burn_rate, 2),
        'weekly_burn_rate': round(weekly_burn_rate, 2),
        'monthly_burn_rate': round(monthly_burn_rate, 2),
        'runway_days': runway_days,
        'category_insights': category_insights,
        'recommendations': recommendations,
        'total_suggested_budget': round(total_suggested_budget, 2),
        'additional_funds_needed': round(additional_funds_needed, 2),
        'spending_trend_labels': json.dumps(spending_trend_labels),
        'spending_trend_values': json.dumps(spending_trend_values),
    }
    
    return render(request, 'tedx_finance/budget_suggestions.html', context)
@login_required
def transactions_table(request):
    """Excel-like table view with inline editing capabilities"""
    user_is_treasurer = is_in_group(request.user, 'Treasurer')
    transactions = Transaction.objects.all().order_by('-date')
    
    # Dynamic categories merged with defaults for filters
    try:
        dynamic = list(Category.objects.all().values_list('name', 'name'))
    except Exception:
        dynamic = []
    default_choices = list(getattr(Transaction, 'CATEGORY_CHOICES', []))
    seen = set()
    categories = []
    for val, label in dynamic + default_choices:
        if val not in seen:
            categories.append((val, label))
            seen.add(val)

    context = {
        'transactions': transactions,
        'categories': categories,
        'is_treasurer': user_is_treasurer,
    }
    return render(request, 'tedx_finance/transactions_table.html', context)

@login_required
def dashboard(request):
    """
    Dashboard view with analytics, charts, recent transactions, and sponsor tiers.
    Supports optional date range filtering via GET parameters.
    """
    context = {}
    try:
        user_is_treasurer = is_in_group(request.user, 'Treasurer')

        # Parse optional date range filters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

        # Income aggregates (respect date range if provided)
        mf_qs = ManagementFund.objects.all()
        sp_qs = Sponsor.objects.all()
        if start_date:
            mf_qs = mf_qs.filter(date_received__gte=start_date)
            sp_qs = sp_qs.filter(date_received__gte=start_date)
        if end_date:
            mf_qs = mf_qs.filter(date_received__lte=end_date)
            sp_qs = sp_qs.filter(date_received__lte=end_date)

        management_funds = mf_qs.aggregate(total=Sum('amount'))['total'] or 0
        sponsor_funds = sp_qs.aggregate(total=Sum('amount'))['total'] or 0
        total_funds = management_funds + sponsor_funds

        # Approved transactions with optional date filters
        approved_transactions = Transaction.objects.filter(approved=True)
        if start_date:
            approved_transactions = approved_transactions.filter(date__gte=start_date)
        if end_date:
            approved_transactions = approved_transactions.filter(date__lte=end_date)

        total_spent_val = approved_transactions.filter(amount__lt=0).aggregate(total=Sum('amount'))['total'] or 0
        total_spent = abs(total_spent_val)
        remaining_balance = total_funds - total_spent

        # Chart Data - Category spending (expenses only)
        category_spending = list(
            approved_transactions.filter(amount__lt=0)
            .values('category')
            .annotate(total=Sum('amount'))
            .order_by('category')
        )

        # Convert category codes to human labels
        category_map = dict(getattr(Transaction, 'CATEGORY_CHOICES', []))
        for item in category_spending:
            # If not in default map, keep the raw category string (user-defined)
            item['category'] = category_map.get(item['category'], item['category'])

        income_data = [float(management_funds), float(sponsor_funds)]

        # Recent and Pending Transactions
        transactions = approved_transactions.order_by('-date')[:10]
        pending_transactions = Transaction.objects.filter(approved=False).order_by('-date')

        # Sponsor tiers (within selected date range)
        sponsors_qs = sp_qs.order_by('-amount')
        sponsors_with_tiers = []
        for s in sponsors_qs:
            tier, badge_class = get_sponsor_tier(s.amount)
            sponsors_with_tiers.append({
                'name': s.name,
                'amount': float(s.amount),
                'tier': tier,
                'badge_class': badge_class,
            })

        # Spending Trends: within selected range, else last 6 months
        if start_date or end_date:
            trend_qs = approved_transactions.filter(amount__lt=0)
        else:
            six_months_ago = datetime.now().date() - timedelta(days=180)
            trend_qs = approved_transactions.filter(amount__lt=0, date__gte=six_months_ago)

        monthly_spending = (
            trend_qs
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        spending_months = [item['month'].strftime('%b %Y') for item in monthly_spending]
        spending_amounts = [abs(float(item['total'])) for item in monthly_spending]

        context = {
            'user': request.user,
            'total_funds': total_funds,
            'total_spent': total_spent,
            'remaining_balance': remaining_balance,
            'transactions': transactions,
            'pending_transactions': pending_transactions,
            'category_spending': category_spending,
            'income_data': income_data,
            'is_treasurer': user_is_treasurer,
            'spending_months': spending_months,
            'spending_amounts': spending_amounts,
            'start_date': start_date_str or '',
            'end_date': end_date_str or '',
            'sponsors_with_tiers': sponsors_with_tiers,
            'management_funds_list': mf_qs.order_by('-date_received'),
            'sponsors_list': sp_qs.order_by('-date_received'),
        }
    except Exception as e:
        context['error'] = f"An unexpected error occurred: {e}"
        logger.error(f"Error in dashboard view: {e}", exc_info=True)

    return render(request, 'tedx_finance/dashboard.html', context)


@login_required
def finance_report(request):
    """
    Printable finance report view with optional date range filters.
    Shows all approved transactions, sponsors, and financial summary.
    """
    try:
        # Parse optional date filters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

        # Income within range
        mf_qs = ManagementFund.objects.all()
        sp_qs = Sponsor.objects.all()
        if start_date:
            mf_qs = mf_qs.filter(date_received__gte=start_date)
            sp_qs = sp_qs.filter(date_received__gte=start_date)
        if end_date:
            mf_qs = mf_qs.filter(date_received__lte=end_date)
            sp_qs = sp_qs.filter(date_received__lte=end_date)

        total_income = (mf_qs.aggregate(total=Sum('amount'))['total'] or 0) + (sp_qs.aggregate(total=Sum('amount'))['total'] or 0)

        # Sponsor tiers list within selected date range
        sponsors_with_tiers = [
            {
                'name': s.name,
                'amount': float(s.amount),
                'tier': get_sponsor_tier(s.amount)[0]
            }
            for s in sp_qs.order_by('-amount')
        ]

        # Approved transactions within range
        tx_qs = Transaction.objects.filter(approved=True)
        if start_date:
            tx_qs = tx_qs.filter(date__gte=start_date)
        if end_date:
            tx_qs = tx_qs.filter(date__lte=end_date)
        tx_qs = tx_qs.order_by('date')

        total_spent_val = tx_qs.filter(amount__lt=0).aggregate(total=Sum('amount'))['total'] or 0
        total_spent = abs(total_spent_val)
        net_balance = total_income - total_spent

        context = {
            'transactions': tx_qs,
            'total_income': total_income,
            'total_spent': total_spent,
            'net_balance': net_balance,
            'start_date': start_date_str or '',
            'end_date': end_date_str or '',
            'sponsors_with_tiers': sponsors_with_tiers,
        }
    except Exception as e:
        context = {'transactions': [], 'total_income': 0, 'total_spent': 0, 'net_balance': 0, 'error': str(e)}
    return render(request, 'tedx_finance/finance_report.html', context)


@login_required
def export_transactions_pdf(request):
    """
    Export financial report as PDF using xhtml2pdf.
    
    Features:
    - Optional date range filtering via GET parameters
    - Includes sponsors with tier classification
    - Shows approved transactions only
    - Includes proof images for transactions
    - Comprehensive error handling with user-friendly messages
    
    Args:
        request: HTTP request with optional start_date and end_date GET parameters
        
    Returns:
        HttpResponse with PDF attachment or error message
    """
    from xhtml2pdf import pisa
    from django.template.loader import render_to_string
    from django.http import HttpResponse
    import io
    import logging
    import os
    
    logger = logging.getLogger(__name__)
    
    # Parse date filters
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    start_date = parse_date(start_date_str)
    end_date = parse_date(end_date_str)
    
    try:
        # Sponsors with date filtering
        sp_qs = Sponsor.objects.all()
        mf_qs = ManagementFund.objects.all()
        if start_date:
            sp_qs = sp_qs.filter(date_received__gte=start_date)
            mf_qs = mf_qs.filter(date_received__gte=start_date)
        if end_date:
            sp_qs = sp_qs.filter(date_received__lte=end_date)
            mf_qs = mf_qs.filter(date_received__lte=end_date)
        
        sponsor_income = sp_qs.aggregate(total=Sum('amount'))['total'] or 0
        management_income = mf_qs.aggregate(total=Sum('amount'))['total'] or 0
        total_income = sponsor_income + management_income
        
        sponsors_with_tiers = [
            {
                'name': s.name,
                'amount': float(s.amount),
                'tier': get_sponsor_tier(s.amount)[0]
            }
            for s in sp_qs.order_by('-amount')
        ]
        
        # Approved transactions with date filtering
        tx_qs = Transaction.objects.filter(approved=True)
        if start_date:
            tx_qs = tx_qs.filter(date__gte=start_date)
        if end_date:
            tx_qs = tx_qs.filter(date__lte=end_date)
        tx_qs = tx_qs.order_by('date')
        
        # Calculate totals
        total_spent_val = tx_qs.filter(amount__lt=0).aggregate(total=Sum('amount'))['total'] or 0
        total_spent = abs(total_spent_val)
        net_balance = total_income - total_spent
        
        # Check if there's data to export
        if not tx_qs.exists() and not sp_qs.exists():
            messages.warning(request, '⚠️ No data found for the selected date range.')
            return redirect('finance_report')
        
        context = {
            'transactions': tx_qs,
            'total_income': total_income,
            'total_spent': total_spent,
            'net_balance': net_balance,
            'start_date': start_date_str or '',
            'end_date': end_date_str or '',
            'sponsors_with_tiers': sponsors_with_tiers,
            'for_pdf': True,
        }
        
    except Exception as e:
        logger.error(f"Error preparing PDF export data: {str(e)}", exc_info=True)
        messages.error(request, f'❌ Error preparing report data: {str(e)}')
        return redirect('tedx_finance:dashboard')
    
    try:
        # Render HTML template
        html_string = render_to_string('tedx_finance/finance_report.html', context, request=request)
        
        # Generate PDF using xhtml2pdf
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html_string.encode("UTF-8")), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f'tedx_finance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            logger.error(f"xhtml2pdf error: {pdf.err}")
            messages.error(request, '❌ Error generating PDF. Please check the report template.')
            return redirect('tedx_finance:dashboard')
            
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}", exc_info=True)
        messages.error(request, f'❌ Failed to generate PDF: {str(e)}')
        return redirect('tedx_finance:dashboard')


# --- Transaction Management ---
@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.created_by = request.user
            transaction.save()
            messages.success(request, 'Transaction submitted for approval!')
            return redirect('tedx_finance:dashboard')
    else:
        form = TransactionForm(request.user)
    context = {
        'form': form,
        'form_title': 'Add a New Transaction',
        'form_button': 'Save Transaction',
        'is_treasurer': is_in_group(request.user, 'Treasurer'),
    }
    return render(request, 'tedx_finance/add_transaction.html', context)

@permission_required('tedx_finance.change_transaction', raise_exception=True)
def approve_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        transaction.approved = True
        transaction.save()
        messages.success(request, f"Transaction '{transaction.title}' approved.")
    return redirect('tedx_finance:dashboard')

@permission_required('tedx_finance.change_transaction', raise_exception=True)
def edit_transaction(request, pk):
    """Edit an existing transaction (treasurers only, audit trail via history)."""
    tx = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        form = TransactionForm(request.user, request.POST, request.FILES, instance=tx)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully.')
            return redirect('tedx_finance:transactions_table')
    else:
        form = TransactionForm(request.user, instance=tx)
    return render(request, 'tedx_finance/add_transaction.html', {
        'form': form,
        'form_title': f"Edit Transaction: {tx.title}",
        'form_button': 'Update Transaction'
    })

@permission_required('tedx_finance.delete_transaction', raise_exception=True)
def reject_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        title = transaction.title
        transaction.delete()
        messages.warning(request, f"Transaction '{title}' has been rejected and deleted.")
    return redirect('tedx_finance:dashboard')

@permission_required('tedx_finance.change_transaction', raise_exception=True)
def bulk_approve_transactions(request):
    """Bulk approve multiple transactions."""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            transaction_ids = data.get('ids', [])
            
            if not transaction_ids:
                return JsonResponse({'success': False, 'error': 'No transaction IDs provided'}, status=400)
            
            # Approve all transactions
            transactions = Transaction.objects.filter(pk__in=transaction_ids)
            count = transactions.update(approved=True)
            
            return JsonResponse({
                'success': True,
                'count': count,
                'message': f'{count} transaction(s) approved successfully'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@permission_required('tedx_finance.delete_transaction', raise_exception=True)
def bulk_reject_transactions(request):
    """Bulk reject (delete) multiple transactions."""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            transaction_ids = data.get('ids', [])
            
            if not transaction_ids:
                return JsonResponse({'success': False, 'error': 'No transaction IDs provided'}, status=400)
            
            # Delete all transactions
            transactions = Transaction.objects.filter(pk__in=transaction_ids)
            count = transactions.count()
            transactions.delete()
            
            return JsonResponse({
                'success': True,
                'count': count,
                'message': f'{count} transaction(s) rejected and deleted successfully'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

# --- Income Management ---
@permission_required('tedx_finance.add_managementfund', raise_exception=True)
def add_management_fund(request):
    if request.method == 'POST':
        form = ManagementFundForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Management fund updated!')
            return redirect('tedx_finance:dashboard')
    else:
        form = ManagementFundForm()
    context = {'form': form, 'form_title': 'Add Management Fund', 'form_button': 'Save Fund'}
    return render(request, 'tedx_finance/add_management_fund.html', context)

@permission_required('tedx_finance.change_managementfund', raise_exception=True)
def edit_management_fund(request, pk):
    """Edit an existing management fund (treasurers only)."""
    fund = get_object_or_404(ManagementFund, pk=pk)
    if request.method == 'POST':
        form = ManagementFundForm(request.POST, instance=fund)
        if form.is_valid():
            form.save()
            messages.success(request, 'Management fund updated successfully.')
            return redirect('tedx_finance:dashboard')
    else:
        form = ManagementFundForm(instance=fund)
    return render(request, 'tedx_finance/add_management_fund.html', {
        'form': form,
        'form_title': f"Edit Management Fund: ₹{fund.amount}",
        'form_button': 'Update Fund'
    })

@permission_required('tedx_finance.delete_managementfund', raise_exception=True)
def delete_management_fund(request, pk):
    """Delete a management fund entry (treasurers only)."""
    fund = get_object_or_404(ManagementFund, pk=pk)
    if request.method == 'POST':
        amount = fund.amount
        fund.delete()
        messages.warning(request, f'Management fund of ₹{amount} has been deleted.')
    return redirect('tedx_finance:dashboard')

@permission_required('tedx_finance.add_sponsor', raise_exception=True)
def add_sponsor(request):
    if request.method == 'POST':
        form = SponsorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'New sponsor added successfully!')
            return redirect('tedx_finance:dashboard')
    else:
        form = SponsorForm()
    context = {'form': form, 'form_title': 'Add New Sponsor', 'form_button': 'Save Sponsor'}
    return render(request, 'tedx_finance/add_sponsor.html', context)

@permission_required('tedx_finance.change_sponsor', raise_exception=True)
def edit_sponsor(request, pk):
    """Edit an existing sponsor (treasurers only)."""
    sponsor = get_object_or_404(Sponsor, pk=pk)
    if request.method == 'POST':
        form = SponsorForm(request.POST, request.FILES, instance=sponsor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sponsor updated successfully.')
            return redirect('tedx_finance:dashboard')
    else:
        form = SponsorForm(instance=sponsor)
    return render(request, 'tedx_finance/add_sponsor.html', {
        'form': form,
        'form_title': f"Edit Sponsor: {sponsor.name}",
        'form_button': 'Update Sponsor'
    })

@permission_required('tedx_finance.delete_sponsor', raise_exception=True)
def delete_sponsor(request, pk):
    """Delete a sponsor entry (treasurers only)."""
    sponsor = get_object_or_404(Sponsor, pk=pk)
    if request.method == 'POST':
        name = sponsor.name
        sponsor.delete()
        messages.warning(request, f'Sponsor "{name}" has been deleted.')
    return redirect('tedx_finance:dashboard')

# --- Exports ---
@login_required
def export_transactions_xlsx(request):
    """
    Export approved transactions to Excel format with optional date filtering.
    
    Features:
    - Exports only approved transactions
    - Optional date range filtering
    - Formatted Excel with headers and proper column widths
    - Includes transaction metadata (date, title, category, amount, submitter)
    - Comprehensive error handling
    
    Args:
        request: HTTP request with optional start_date and end_date GET parameters
        
    Returns:
        HttpResponse with Excel attachment or redirect with error message
    """
    import logging
    from openpyxl.styles import Font, Alignment, PatternFill
    from openpyxl.utils import get_column_letter
    
    logger = logging.getLogger(__name__)
    
    try:
        # Parse optional filters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

        # Query approved transactions
        transactions = Transaction.objects.filter(approved=True)
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)
        transactions = transactions.order_by('date')
        
        # Check if there's data to export
        if not transactions.exists():
            messages.warning(request, '⚠️ No approved transactions found for the selected date range.')
            return redirect('tedx_finance:transactions_table')
        
        # Create Excel workbook
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        filename = f'tedx_transactions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = 'Transactions'
        
        # Header row with styling
        columns = ['Date', 'Title', 'Category', 'Amount', 'Submitted By']
        worksheet.append(columns)
        
        # Style header row
        header_fill = PatternFill(start_color='4F46E5', end_color='4F46E5', fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF', size=12)
        for col_num, column_title in enumerate(columns, 1):
            cell = worksheet.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Data rows
        for tx in transactions:
            row = [
                tx.date,
                tx.title,
                tx.get_category_display(),
                float(tx.amount),
                tx.created_by.username if tx.created_by else 'N/A'
            ]
            worksheet.append(row)
        
        # Auto-adjust column widths
        for col_num, column_cells in enumerate(worksheet.columns, 1):
            max_length = 0
            column = get_column_letter(col_num)
            for cell in column_cells:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            worksheet.column_dimensions[column].width = adjusted_width
        
        # Add summary row
        row_count = worksheet.max_row
        total_amount = sum(float(tx.amount) for tx in transactions)
        summary_row = [
            '',
            '',
            'TOTAL',
            total_amount,
            f'{transactions.count()} transactions'
        ]
        worksheet.append(summary_row)
        
        # Style summary row
        summary_fill = PatternFill(start_color='E5E7EB', end_color='E5E7EB', fill_type='solid')
        summary_font = Font(bold=True)
        for col_num in range(1, 6):
            cell = worksheet.cell(row=row_count + 1, column=col_num)
            cell.fill = summary_fill
            cell.font = summary_font
        
        workbook.save(response)
        return response
        
    except Exception as e:
        logger.error(f"Error exporting transactions to Excel: {str(e)}", exc_info=True)
        messages.error(request, f'❌ Failed to export Excel file: {str(e)}')
        return redirect('tedx_finance:dashboard')


@login_required
def export_transactions_with_proofs(request):
    """
    Export approved transactions as Excel + all proof images in a ZIP file.
    
    Features:
    - Includes Excel report with transaction data
    - Bundles all proof images organized by transaction
    - Optional date range filtering
    - Creates organized folder structure: proofs/TransactionTitle_Date/
    
    Args:
        request: HTTP request with optional start_date and end_date GET parameters
        
    Returns:
        HttpResponse with ZIP attachment containing Excel + proof images
    """
    import logging
    import zipfile
    import io
    import os
    from openpyxl.styles import Font, Alignment, PatternFill
    from openpyxl.utils import get_column_letter
    from django.core.files.storage import default_storage
    
    logger = logging.getLogger(__name__)
    
    try:
        # Parse optional filters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

        # Query approved transactions
        transactions = Transaction.objects.filter(approved=True)
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)
        transactions = transactions.order_by('date')
        
        if not transactions.exists():
            messages.warning(request, '⚠️ No approved transactions found for the selected date range.')
            return redirect('tedx_finance:transactions_table')
        
        # Create in-memory ZIP file
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # --- 1. Create Excel report ---
            workbook = openpyxl.Workbook()
            worksheet = workbook.active
            worksheet.title = 'Transactions'
            
            # Header row with styling
            columns = ['Date', 'Title', 'Category', 'Amount', 'Submitted By', 'Proof File']
            worksheet.append(columns)
            
            # Style header row
            header_fill = PatternFill(start_color='4F46E5', end_color='4F46E5', fill_type='solid')
            header_font = Font(bold=True, color='FFFFFF', size=12)
            for col_num, column_title in enumerate(columns, 1):
                cell = worksheet.cell(row=1, column=col_num)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Data rows with proof file references
            for tx in transactions:
                proof_filename = ''
                if tx.proof:
                    proof_filename = os.path.basename(tx.proof.name)
                
                row = [
                    tx.date,
                    tx.title,
                    tx.get_category_display(),
                    float(tx.amount),
                    tx.created_by.username if tx.created_by else 'N/A',
                    proof_filename or 'No proof uploaded'
                ]
                worksheet.append(row)
            
            # Auto-adjust column widths
            for col_num, column_cells in enumerate(worksheet.columns, 1):
                max_length = 0
                column = get_column_letter(col_num)
                for cell in column_cells:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column].width = adjusted_width
            
            # Add summary row
            row_count = worksheet.max_row
            total_amount = sum(float(tx.amount) for tx in transactions)
            summary_row = [
                '',
                '',
                'TOTAL',
                total_amount,
                f'{transactions.count()} transactions',
                ''
            ]
            worksheet.append(summary_row)
            
            # Style summary row
            summary_fill = PatternFill(start_color='E5E7EB', end_color='E5E7EB', fill_type='solid')
            summary_font = Font(bold=True)
            for col_num in range(1, 7):
                cell = worksheet.cell(row=row_count + 1, column=col_num)
                cell.fill = summary_fill
                cell.font = summary_font
            
            # Save Excel to buffer
            excel_buffer = io.BytesIO()
            workbook.save(excel_buffer)
            excel_buffer.seek(0)
            
            # Add Excel to ZIP
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_file.writestr(f'tedx_transactions_{timestamp}.xlsx', excel_buffer.read())
            
            # --- 2. Add proof images to ZIP ---
            proofs_added = 0
            for tx in transactions:
                if tx.proof:
                    try:
                        # Create organized folder structure
                        safe_title = "".join(c for c in tx.title if c.isalnum() or c in (' ', '-', '_')).strip()
                        folder_name = f"proofs/{safe_title}_{tx.date}"
                        file_extension = os.path.splitext(tx.proof.name)[1]
                        proof_path = f"{folder_name}/proof{file_extension}"
                        
                        # Read proof file and add to ZIP
                        if default_storage.exists(tx.proof.name):
                            with default_storage.open(tx.proof.name, 'rb') as proof_file:
                                zip_file.writestr(proof_path, proof_file.read())
                                proofs_added += 1
                    except Exception as e:
                        logger.warning(f"Could not add proof for transaction {tx.id}: {str(e)}")
            
            # Add a README file
            readme_content = f"""TEDx Finance Report with Proofs
=====================================

Export Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Date Range: {start_date or 'All'} to {end_date or 'All'}

Contents:
---------
1. tedx_transactions_{timestamp}.xlsx - Full transaction report
2. proofs/ folder - {proofs_added} proof images organized by transaction

File Structure:
---------------
proofs/
  ├── TransactionTitle_Date/
  │   └── proof.jpg (or .pdf, .png, etc.)
  └── ...

Notes:
------
- Only approved transactions are included
- Proof images are organized by transaction title and date
- If a transaction has no proof, it won't appear in the proofs folder
- All amounts are in Indian Rupees (₹)

For questions, contact the TEDx Finance Team.
"""
            zip_file.writestr('README.txt', readme_content)
        
        # Prepare ZIP response
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="tedx_report_with_proofs_{timestamp}.zip"'
        
        messages.success(request, f'✅ Exported {transactions.count()} transactions with {proofs_added} proof files!')
        return response
        
    except Exception as e:
        logger.error(f"Error exporting ZIP with proofs: {str(e)}", exc_info=True)
        messages.error(request, f'❌ Failed to export ZIP file: {str(e)}')
        return redirect('tedx_finance:dashboard')


@permission_required('tedx_finance.add_transaction', raise_exception=True)
def import_transactions(request):
    """
    Bulk import transactions from .xlsx file.
    Validates file type, size (max 5MB), and data format.
    Expected columns: Date, Title, Category, Amount, SubmittedBy (optional)
    """
    report = None
    MAX_FILE_SIZE_MB = 5  # Maximum file size in megabytes
    
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        
        # Validate file type
        if not uploaded_file or not uploaded_file.name.endswith('.xlsx'):
            messages.error(request, 'Please upload a valid .xlsx file.')
        # Validate file size
        elif uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            messages.error(request, f'File size exceeds {MAX_FILE_SIZE_MB}MB limit.')
        else:
            try:
                wb = openpyxl.load_workbook(uploaded_file)
                ws = wb.active
                errors = []
                created = 0
                from django.contrib.auth.models import User
                
                # Process each row (skip header row)
                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not row[0]:  # Skip empty rows
                        continue
                    try:
                        # Parse row data
                        date_val = row[0] if isinstance(row[0], str) else row[0].strftime('%Y-%m-%d') if hasattr(row[0], 'strftime') else str(row[0])
                        title = str(row[1]) if len(row) > 1 and row[1] else ''
                        category = str(row[2]) if len(row) > 2 and row[2] else ''
                        amount = float(row[3]) if len(row) > 3 and row[3] else 0.0
                        username = str(row[4]).strip() if len(row) > 4 and row[4] else None
                        
                        # Validate required fields
                        if not title or not category:
                            errors.append({'row': idx, 'message': 'Missing title or category'})
                            continue
                        
                        # Ensure category exists in Category table (create if missing)
                        if category:
                            try:
                                Category.objects.get_or_create(name=category)
                            except Exception:
                                pass
                        
                        # Find or default user
                        user = None
                        if username:
                            try:
                                user = User.objects.get(username=username)
                            except User.DoesNotExist:
                                pass
                        if not user:
                            user = request.user
                        
                        # Create transaction
                        Transaction.objects.create(
                            title=title,
                            amount=amount,
                            category=category,
                            date=date_val,
                            created_by=user,
                            approved=False
                        )
                        created += 1
                    except Exception as e:
                        errors.append({'row': idx, 'message': str(e)})
                
                report = {'created': created, 'errors': errors}
                if created > 0:
                    messages.success(request, f'{created} transactions imported successfully.')
                if errors:
                    messages.warning(request, f'{len(errors)} rows had errors.')
            except Exception as e:
                messages.error(request, f'Error reading file: {e}')
    
    try:
        dynamic = list(Category.objects.all().values_list('name', 'name'))
    except Exception:
        dynamic = []
    default_choices = list(getattr(Transaction, 'CATEGORY_CHOICES', []))
    seen = set()
    categories = []
    for val, label in dynamic + default_choices:
        if val not in seen:
            categories.append((val, label))
            seen.add(val)

    context = {
        'categories': categories,
        'report': report,
    }
    return render(request, 'tedx_finance/import_transactions.html', context)


@login_required
def manage_categories(request):
    """Simple manager to add/remove custom categories (Treasurer only)."""
    user_is_treasurer = is_in_group(request.user, 'Treasurer')
    if not user_is_treasurer:
        messages.error(request, 'Only treasurers can manage categories.')
        return redirect('tedx_finance:dashboard')

    # Add new category
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        if not name:
            messages.error(request, 'Category name cannot be empty.')
        elif len(name) > 50:
            messages.error(request, 'Category name must be 50 characters or fewer.')
        else:
            obj, created = Category.objects.get_or_create(name=name)
            if created:
                messages.success(request, f'Category "{name}" added.')
            else:
                messages.info(request, f'Category "{name}" already exists.')
        return redirect('tedx_finance:manage_categories')

    # Delete category
    delete_id = request.GET.get('delete')
    if delete_id:
        try:
            cat = Category.objects.get(id=delete_id)
            cat.delete()
            messages.warning(request, f'Category "{cat.name}" deleted.')
            return redirect('tedx_finance:manage_categories')
        except Category.DoesNotExist:
            messages.error(request, 'Category not found.')

    categories = Category.objects.all()
    return render(request, 'tedx_finance/manage_categories.html', {
        'categories': categories,
        'is_treasurer': user_is_treasurer,
    })


@login_required
def proof_gallery(request):
    """
    Gallery view of all transaction proofs with thumbnails and lightbox.
    Shows only approved transactions with uploaded proof files.
    Includes filtering by category and date range.
    """
    user_is_treasurer = is_in_group(request.user, 'Treasurer')
    
    # Parse optional filters
    category_filter = request.GET.get('category', '')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    tx_id_param = request.GET.get('tx_id', '')  # For auto-opening specific transaction
    start_date = parse_date(start_date_str)
    end_date = parse_date(end_date_str)
    
    # Query transactions with proofs
    transactions = Transaction.objects.filter(approved=True, proof__isnull=False).exclude(proof='')
    
    if category_filter:
        transactions = transactions.filter(category=category_filter)
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
    
    transactions = transactions.order_by('-date')
    
    # Get unique categories for filter dropdown
    try:
        dynamic = list(Category.objects.all().values_list('name', 'name'))
    except Exception:
        dynamic = []
    default_choices = list(getattr(Transaction, 'CATEGORY_CHOICES', []))
    seen = set()
    categories = []
    for val, label in dynamic + default_choices:
        if val not in seen:
            categories.append((val, label))
            seen.add(val)
    
    context = {
        'transactions': transactions,
        'categories': categories,
        'category_filter': category_filter,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'tx_id_param': tx_id_param,
        'is_treasurer': user_is_treasurer,
    }
    return render(request, 'tedx_finance/proof_gallery.html', context)


@login_required
def quick_add_category(request):
    """AJAX: quick add a new Category (Treasurer only)."""
    if not is_in_group(request.user, 'Treasurer'):
        return JsonResponse({'success': False, 'error': 'Forbidden'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
    import json
    try:
        data = json.loads(request.body or '{}')
        name = (data.get('name') or '').strip()
        if not name:
            return JsonResponse({'success': False, 'error': 'Name is required'}, status=400)
        if len(name) > 50:
            return JsonResponse({'success': False, 'error': 'Name must be <= 50 chars'}, status=400)
        cat, created = Category.objects.get_or_create(name=name)
        # Build merged categories list (dynamic + defaults) preserving order
        try:
            dynamic = list(Category.objects.all().values_list('name', 'name'))
        except Exception:
            dynamic = []
        default_choices = list(getattr(Transaction, 'CATEGORY_CHOICES', []))
        seen = set()
        merged = []
        for val, label in dynamic + default_choices:
            if val not in seen:
                merged.append({'value': val, 'label': label})
                seen.add(val)
        return JsonResponse({'success': True, 'id': cat.id, 'name': cat.name, 'categories': merged})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def quick_rename_category(request):
    """AJAX: rename a Category and cascade to Transaction.category strings (Treasurer only)."""
    if not is_in_group(request.user, 'Treasurer'):
        return JsonResponse({'success': False, 'error': 'Forbidden'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
    import json
    try:
        data = json.loads(request.body or '{}')
        cat_id = data.get('id')
        old_name = (data.get('old_name') or '').strip()
        new_name = (data.get('new_name') or '').strip()
        if not new_name:
            return JsonResponse({'success': False, 'error': 'New name is required'}, status=400)
        if len(new_name) > 50:
            return JsonResponse({'success': False, 'error': 'Name must be <= 50 chars'}, status=400)
        # Check conflict
        if Category.objects.filter(name=new_name).exclude(id=cat_id).exists():
            return JsonResponse({'success': False, 'error': 'Category with this name already exists'}, status=409)
        cat = None
        if cat_id:
            cat = Category.objects.filter(id=cat_id).first()
        if not cat and old_name:
            cat, _ = Category.objects.get_or_create(name=old_name)
        if not cat:
            return JsonResponse({'success': False, 'error': 'Category not found'}, status=404)
        # Rename
        prev_name = cat.name
        cat.name = new_name
        cat.save()
        # Update Transaction rows that used the old string value
        Transaction.objects.filter(category=prev_name).update(category=new_name)
        # Build merged list
        try:
            dynamic = list(Category.objects.all().values_list('name', 'name'))
        except Exception:
            dynamic = []
        default_choices = list(getattr(Transaction, 'CATEGORY_CHOICES', []))
        seen = set()
        merged = []
        for val, label in dynamic + default_choices:
            if val not in seen:
                merged.append({'value': val, 'label': label})
                seen.add(val)
        return JsonResponse({'success': True, 'id': cat.id, 'name': cat.name, 'categories': merged})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

