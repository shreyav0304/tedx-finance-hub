"""
Test script to verify export functionality.
Run this after starting the Django development server.
"""
import os
import sys
from datetime import date, timedelta

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realtime_tedx.settings')

import django
django.setup()

from tedx_finance.models import Transaction, Sponsor, ManagementFund
from django.contrib.auth.models import User

def create_test_data():
    """Create sample test data for exports."""
    print("🔧 Creating test data...")
    
    # Create a test user if doesn't exist
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'is_staff': True}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("✅ Created test user: testuser")
    
    # Create management fund
    fund, created = ManagementFund.objects.get_or_create(
        amount=10000,
        defaults={'date_received': date.today() - timedelta(days=30)}
    )
    if created:
        print(f"✅ Created management fund: ₹{fund.amount}")
    
    # Create sponsors
    sponsors_data = [
        {'name': 'Tech Corp', 'amount': 50000, 'contact_email': 'tech@corp.com'},
        {'name': 'Innovation Labs', 'amount': 30000, 'contact_email': 'info@labs.com'},
        {'name': 'Future Systems', 'amount': 15000, 'contact_email': 'contact@future.com'},
    ]
    
    for sponsor_data in sponsors_data:
        sponsor, created = Sponsor.objects.get_or_create(
            name=sponsor_data['name'],
            defaults={
                'amount': sponsor_data['amount'],
                'date_received': date.today() - timedelta(days=20),
                'contact_email': sponsor_data['contact_email']
            }
        )
        if created:
            print(f"✅ Created sponsor: {sponsor.name} - ₹{sponsor.amount}")
    
    # Create transactions
    transactions_data = [
        {'title': 'Venue booking deposit', 'amount': -5000, 'category': 'Venue'},
        {'title': 'Marketing materials', 'amount': -2000, 'category': 'Marketing'},
        {'title': 'Speaker travel', 'amount': -3000, 'category': 'Speakers'},
        {'title': 'Stage setup', 'amount': -1500, 'category': 'Logistics'},
        {'title': 'Social media ads', 'amount': -1000, 'category': 'Marketing'},
    ]
    
    for tx_data in transactions_data:
        tx, created = Transaction.objects.get_or_create(
            title=tx_data['title'],
            defaults={
                'amount': tx_data['amount'],
                'category': tx_data['category'],
                'date': date.today() - timedelta(days=10),
                'created_by': user,
                'approved': True  # Approved so they show in exports
            }
        )
        if created:
            print(f"✅ Created transaction: {tx.title} - ₹{tx.amount}")
    
    print("\n✅ Test data creation complete!")
    print(f"📊 Total Sponsors: {Sponsor.objects.count()}")
    print(f"📊 Total Transactions: {Transaction.objects.count()}")
    print(f"📊 Approved Transactions: {Transaction.objects.filter(approved=True).count()}")

def verify_export_views():
    """Verify export views are working."""
    print("\n🔍 Verifying export views...")
    
    try:
        from tedx_finance.views import export_transactions_pdf, export_transactions_xlsx
        print("✅ Export views imported successfully")
        
        # Check if xhtml2pdf is installed
        try:
            import xhtml2pdf
            print("✅ xhtml2pdf library found")
        except ImportError:
            print("⚠️  xhtml2pdf not installed. PDF export may not work.")
            print("   Install with: pip install xhtml2pdf")
        
        # Check if openpyxl is installed
        try:
            import openpyxl
            print("✅ openpyxl library found")
        except ImportError:
            print("⚠️  openpyxl not installed. Excel export may not work.")
            print("   Install with: pip install openpyxl")
        
    except Exception as e:
        print(f"❌ Error importing export views: {e}")

def print_export_urls():
    """Print the URLs for testing exports."""
    print("\n📋 Export URLs for testing:")
    print("="*60)
    print("Excel Export (all): http://127.0.0.1:8000/export/excel/")
    print("PDF Export (all):   http://127.0.0.1:8000/export/pdf/")
    print("\nWith date filters:")
    print("Excel Export: http://127.0.0.1:8000/export/excel/?start_date=2025-01-01&end_date=2025-12-31")
    print("PDF Export:   http://127.0.0.1:8000/export/pdf/?start_date=2025-01-01&end_date=2025-12-31")
    print("="*60)

if __name__ == '__main__':
    print("🚀 TEDx Finance Hub - Export Testing")
    print("="*60)
    
    verify_export_views()
    create_test_data()
    print_export_urls()
    
    print("\n✅ All checks complete!")
    print("📝 To test exports:")
    print("   1. Start the development server: python manage.py runserver")
    print("   2. Login with: testuser / testpass123")
    print("   3. Visit the URLs above to test exports")
    print("   4. Check your downloads folder for exported files")
