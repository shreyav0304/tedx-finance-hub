from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth

from .models import ManagementFund, Sponsor, Transaction
from .forms import TransactionForm, ManagementFundForm, SponsorForm

import openpyxl


# --- Helper functions ---
def is_in_group(user, group_name):
    """
    Checks if a user is in a given group.
    """
    if user.is_authenticated:
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
    budgets = Budget.objects.all().order_by('category')
    context = {
        'budgets': budgets,
        'is_treasurer': user_is_treasurer,
    }
    return render(request, 'tedx_finance/budgets.html', context)
@login_required
def transactions_table(request):
    """Excel-like table view with inline editing capabilities"""
    user_is_treasurer = is_in_group(request.user, 'Treasurer')
    transactions = Transaction.objects.all().order_by('-date')
    
    context = {
        'transactions': transactions,
        'categories': Transaction.CATEGORY_CHOICES,
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
        category_map = dict(Transaction.CATEGORY_CHOICES)
        for item in category_spending:
            item['category'] = category_map.get(item['category'], 'Unknown')

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
        print(f"ERROR IN DASHBOARD VIEW: {e}")

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
    context = {'form': form, 'form_title': 'Add a New Transaction', 'form_button': 'Save Transaction'}
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
                        
                        # Validate category
                        valid_categories = [c[0] for c in Transaction.CATEGORY_CHOICES]
                        if category not in valid_categories:
                            errors.append({'row': idx, 'message': f'Invalid category: {category}'})
                            continue
                        
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
    
    context = {
        'categories': Transaction.CATEGORY_CHOICES,
        'report': report,
    }
    return render(request, 'tedx_finance/import_transactions.html', context)

