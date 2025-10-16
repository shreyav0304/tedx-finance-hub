# 📊 Export Features Documentation

## Overview
The TEDx Finance Hub includes robust export functionality for financial reports and transactions in both Excel and PDF formats.

---

## 🚀 Features

### Excel Export (`export_transactions_xlsx`)
- **Format**: `.xlsx` (Microsoft Excel)
- **Styling**: Professional formatting with colored headers and auto-adjusted column widths
- **Content**: All approved transactions with metadata
- **Summary**: Total row with transaction count and amount sum
- **Date Filtering**: Optional `start_date` and `end_date` query parameters

#### Features:
✅ Purple header row with white text  
✅ Auto-adjusted column widths (capped at 50 characters)  
✅ Summary row with totals  
✅ Timestamp in filename for uniqueness  
✅ Comprehensive error handling with user feedback  
✅ Empty data validation (warns if no data to export)  

#### Columns Exported:
1. **Date** - Transaction date
2. **Title** - Transaction description
3. **Category** - Expense category (Marketing, Logistics, etc.)
4. **Amount** - Transaction amount in currency
5. **Submitted By** - Username who created the transaction

---

### PDF Export (`export_transactions_pdf`)
- **Format**: `.pdf` (Portable Document Format)
- **Library**: xhtml2pdf
- **Content**: Financial report with transactions and sponsors
- **Styling**: TED Red branding, clean tables, summary section
- **Date Filtering**: Optional `start_date` and `end_date` query parameters

#### Features:
✅ TED Red color scheme  
✅ Financial summary with income, spent, and balance  
✅ Transactions table with color-coded amounts (red for expenses, green for income)  
✅ Sponsors table with tier classification  
✅ Timestamp in filename  
✅ Comprehensive error handling with logging  
✅ Empty data validation  

#### Sections Included:
1. **Header** - Report title and date range
2. **Financial Summary** - Total income, total spent, net balance
3. **Transactions Table** - All approved transactions
4. **Sponsors Table** - All sponsors with tier classification

---

## 🔗 API Endpoints

### Export Excel
```
GET /export/excel/
GET /export/excel/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```

**Example:**
```
http://127.0.0.1:8000/export/excel/
http://127.0.0.1:8000/export/excel/?start_date=2025-01-01&end_date=2025-12-31
```

### Export PDF
```
GET /export/pdf/
GET /export/pdf/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```

**Example:**
```
http://127.0.0.1:8000/export/pdf/
http://127.0.0.1:8000/export/pdf/?start_date=2025-01-01&end_date=2025-12-31
```

---

## 📱 User Interface

### Dashboard Export Buttons
The dashboard includes a dropdown menu with export options:
- **Export Excel** - Green button with Excel icon
- **Export PDF** - Red button with PDF icon
- Both buttons automatically include current date filter parameters

### Transactions Table Export
The transactions table page includes:
- **Export Excel** button in the header (exports all approved transactions)
- **Export Selected** button for bulk operations (exports selected transactions)

---

## 🛡️ Error Handling

### Excel Export Errors
1. **No Data Found**: Displays warning message and redirects to transactions table
2. **Export Failure**: Logs error, displays error message, and redirects
3. **File Generation Error**: Catches exceptions and provides user-friendly feedback

### PDF Export Errors
1. **No Data Found**: Displays warning message and redirects to finance report
2. **Data Preparation Error**: Logs error with traceback and redirects
3. **PDF Generation Error**: Logs xhtml2pdf errors and provides feedback
4. **Template Rendering Error**: Catches exceptions and displays error message

### User Feedback
All export operations provide feedback through Django messages:
- ✅ **Success**: Green message with filename
- ⚠️ **Warning**: Yellow message for no data
- ❌ **Error**: Red message with error description

---

## 🔧 Technical Details

### Dependencies
```python
# Excel Export
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

# PDF Export
from xhtml2pdf import pisa
from django.template.loader import render_to_string
```

### File Naming Convention
- **Excel**: `tedx_transactions_YYYYMMDD_HHMMSS.xlsx`
- **PDF**: `tedx_finance_report_YYYYMMDD_HHMMSS.pdf`

### Styling

#### Excel Styling
```python
# Header
header_fill = PatternFill(start_color='4F46E5', end_color='4F46E5', fill_type='solid')
header_font = Font(bold=True, color='FFFFFF', size=12)
header_alignment = Alignment(horizontal='center', vertical='center')

# Summary Row
summary_fill = PatternFill(start_color='E5E7EB', end_color='E5E7EB', fill_type='solid')
summary_font = Font(bold=True)
```

#### PDF Styling
```css
/* TED Red Branding */
h1, h2 { color: #E62B1E; }

/* Tables */
table { width: 100%; border-collapse: collapse; }
th { background-color: #f2f2f2; }

/* Color-coded amounts */
.expense { color: #D9534F; }
.income { color: #5CB85C; }
```

---

## 📊 Data Filters

### Query Parameters
Both export functions accept optional date range filters:

- **start_date**: Filter transactions/sponsors from this date onwards (format: YYYY-MM-DD)
- **end_date**: Filter transactions/sponsors up to this date (format: YYYY-MM-DD)

### Filter Logic
```python
# Parse dates
start_date = parse_date(request.GET.get('start_date'))
end_date = parse_date(request.GET.get('end_date'))

# Apply filters
if start_date:
    queryset = queryset.filter(date__gte=start_date)
if end_date:
    queryset = queryset.filter(date__lte=end_date)
```

---

## 🧪 Testing

### Test Data Creation
Run the test script to create sample data:
```bash
python test_exports.py
```

This creates:
- ✅ Test user (testuser / testpass123)
- ✅ Management fund (₹10,000)
- ✅ 3 sponsors (Tech Corp, Innovation Labs, Future Systems)
- ✅ 5 approved transactions

### Manual Testing
1. Start development server: `python manage.py runserver`
2. Login with test credentials
3. Navigate to Dashboard or Transactions Table
4. Click export buttons
5. Verify downloaded files in Downloads folder

### Test Cases
- ✅ Export all transactions (no filters)
- ✅ Export with date range filter
- ✅ Export with no data (should show warning)
- ✅ Export with invalid date format (should handle gracefully)
- ✅ Verify Excel formatting and formulas
- ✅ Verify PDF rendering and styling

---

## 🔒 Security Considerations

1. **Authentication**: All export views require login (`@login_required` or equivalent)
2. **Data Filtering**: Only approved transactions are exported
3. **File Size**: No explicit file size limit (controlled by database query size)
4. **SQL Injection**: Protected by Django ORM
5. **XSS**: Template auto-escaping enabled

---

## 📈 Performance Optimization

### Excel Export
- **Query Optimization**: Uses `select_related()` for foreign keys
- **Batch Processing**: Appends rows in bulk
- **Column Width Calculation**: Capped at 50 characters to prevent excessive widths

### PDF Export
- **Template Caching**: Django template cache enabled
- **Query Optimization**: Single query per model with aggregation
- **Memory Management**: Uses `io.BytesIO()` for in-memory operations

---

## 🐛 Common Issues & Solutions

### Issue 1: "xhtml2pdf not installed"
**Solution:**
```bash
pip install xhtml2pdf
```

### Issue 2: "openpyxl not installed"
**Solution:**
```bash
pip install openpyxl
```

### Issue 3: PDF rendering issues with special characters
**Solution:** Ensure UTF-8 encoding:
```python
html_string.encode("UTF-8")
```

### Issue 4: Excel column widths too large
**Solution:** Column widths are capped at 50 characters:
```python
adjusted_width = min(max_length + 2, 50)
```

### Issue 5: No data to export
**Solution:** The system automatically detects and warns users:
```python
if not transactions.exists():
    messages.warning(request, '⚠️ No data found')
    return redirect(...)
```

---

## 🔄 Future Enhancements

### Planned Features
- [ ] CSV export format
- [ ] Customizable Excel templates
- [ ] Charts in PDF exports
- [ ] Email export functionality
- [ ] Scheduled/automated exports
- [ ] Multi-sheet Excel exports (separate sheets for categories)
- [ ] Export history tracking
- [ ] Watermarks on PDF exports

### Potential Improvements
- [ ] Progress bar for large exports
- [ ] Background task queue (Celery) for large exports
- [ ] Compression for large files
- [ ] Export presets (templates)
- [ ] Custom column selection

---

## 📞 Support

For issues or questions about export functionality:
1. Check the error logs: `tail -f logs/django.log`
2. Review Django messages for user-friendly error descriptions
3. Verify all dependencies are installed: `pip list`
4. Run the test script: `python test_exports.py`

---

## 📝 Changelog

### Version 2.0 (Current)
- ✅ Enhanced Excel export with professional styling
- ✅ Improved PDF export with comprehensive error handling
- ✅ Added empty data validation
- ✅ Added timestamp to filenames
- ✅ Improved user feedback with Django messages
- ✅ Added logging for debugging
- ✅ Added summary rows in Excel
- ✅ Added sponsor tier classification in PDF

### Version 1.0
- Basic Excel export
- Basic PDF export
- Date range filtering

---

**Last Updated:** October 15, 2025  
**Maintained By:** TEDx Finance Hub Development Team
