from django.urls import path
from . import views

app_name = 'tedx_finance'

urlpatterns = [
    # Auth
    path('signup/', views.signup, name='signup'),

    # Main dashboard
    path('', views.dashboard, name='dashboard'),
    path('budgets/', views.budgets, name='budgets'),
    path('budget-suggestions/', views.budget_suggestions, name='budget_suggestions'),
    
    # Transactions table view
    path('transactions/', views.transactions_table, name='transactions_table'),

    # Transaction forms and approvals
    path('add/', views.add_transaction, name='add_transaction'),
    path('transaction/<int:pk>/edit/', views.edit_transaction, name='edit_transaction'),
    path('transaction/<int:pk>/approve/', views.approve_transaction, name='approve_transaction'),
    path('transaction/<int:pk>/reject/', views.reject_transaction, name='reject_transaction'),
    path('transactions/bulk-approve/', views.bulk_approve_transactions, name='bulk_approve_transactions'),
    path('transactions/bulk-reject/', views.bulk_reject_transactions, name='bulk_reject_transactions'),
    path('import/', views.import_transactions, name='import_transactions'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('categories/quick-add', views.quick_add_category, name='quick_add_category'),
    path('categories/quick-rename', views.quick_rename_category, name='quick_rename_category'),
    path('proofs/', views.proof_gallery, name='proof_gallery'),

    # Income forms
    path('add-fund/', views.add_management_fund, name='add_management_fund'),
    path('fund/<int:pk>/edit/', views.edit_management_fund, name='edit_management_fund'),
    path('fund/<int:pk>/delete/', views.delete_management_fund, name='delete_management_fund'),
    path('add-sponsor/', views.add_sponsor, name='add_sponsor'),
    path('sponsor/<int:pk>/edit/', views.edit_sponsor, name='edit_sponsor'),
    path('sponsor/<int:pk>/delete/', views.delete_sponsor, name='delete_sponsor'),

    # Export URLs
    path('export/excel/', views.export_transactions_xlsx, name='export_xlsx'),
    path('export/pdf/', views.export_transactions_pdf, name='export_pdf'),
    path('export/zip/', views.export_transactions_with_proofs, name='export_zip'),
    path('export/proofs-csv/', views.export_proofs_to_csv, name='export_proofs_csv'),
    path('export/proofs-pdf/', views.export_proofs_to_pdf, name='export_proofs_pdf'),
    path('report/', views.finance_report, name='finance_report'),
    # path('export/pdf/', views.export_transactions_pdf, name='export_pdf'), # Temporarily disabled
]

