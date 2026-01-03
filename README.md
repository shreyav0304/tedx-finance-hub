# TEDx Finance Hub 🎯💰

> **A modern, production-ready financial management system for TEDx events**  
> Built with Django 5.2 | Glassmorphic UI | Real-time collaboration | Professional exports

[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Security](https://img.shields.io/badge/Security-98%2F100-brightgreen.svg)](SECURITY_AUDIT.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Why TEDx Finance Hub?

### 💔 The Problem with Excel:
- ❌ No real-time collaboration (version conflicts)
- ❌ No role-based permissions (everyone edits everything)
- ❌ Manual calculations prone to errors
- ❌ No audit trail (who changed what?)
- ❌ No approval workflows
- ❌ Poor mobile experience
- ❌ Data security concerns

### ✨ Our Solution:
- ✅ **Real-Time Collaboration** - Multiple treasurers work simultaneously
- ✅ **Role-Based Access** - Team members submit, treasurers approve
- ✅ **Automatic Calculations** - Zero formula errors
- ✅ **Complete Audit Trail** - Track every change with django-simple-history
- ✅ **Professional Exports** - Styled Excel & PDF reports
- ✅ **Beautiful Dashboard** - Interactive charts with Chart.js
- ✅ **Mobile-First Design** - Works perfectly on all devices
- ✅ **Secure & Compliant** - OWASP best practices, 98/100 security score

---

## 🎨 Features Overview

### 🖥️ Modern UI/UX
- **Glassmorphism Design** - Beautiful frosted glass effects
- **Dark/Light Theme Toggle** - Respects system preferences
- **Gradient Backgrounds** - Eye-catching purple-to-blue gradients
- **Tailwind CSS** - Responsive, mobile-first styling
- **Interactive Charts** - Real-time financial visualizations
- **Smooth Animations** - Professional transitions and effects

### 💼 Financial Management
- **Transaction Tracking** - Add, edit, approve expenses with receipts
- **Budget Management** - Set budgets per category with alerts
- **Sponsor Management** - Track sponsorships with tier classification
- **Management Funds** - Record initial funding from organization
- **Inline Editing** - Click any cell to edit (Excel-like)
- **Bulk Operations** - Select multiple transactions, approve/reject/export at once
- **Proof Gallery** - Searchable proofs with bulk drag-and-drop uploads and auto-matching
- **Notifications & Alerts** - Real-time bell badge plus API for unread counts
- **User Settings** - Per-user theme and email notification preferences

### 📊 Reports & Analytics
- **Financial Dashboard** - Income, expenses, balance, trends
- **Category Breakdown** - Pie charts showing spending by category
- **Monthly Trends** - Line charts tracking expenses over time
- **Budget Utilization** - Progress bars with color-coded alerts
- **Excel Export** - Professional `.xlsx` with styling and formulas
- **PDF Reports** - Branded reports with TED Red color scheme

### 🔒 Security & Compliance
- **Authentication Required** - Django's built-in auth system
- **Permission-Based Actions** - Treasurers vs team members
- **Audit Trail** - Complete history of all changes
- **File Upload Validation** - Size limits (5MB) and type checking
- **CSRF Protection** - Enabled by default
- **SQL Injection Safe** - Django ORM protects against attacks
- **XSS Protection** - Template auto-escaping enabled

---

## 📦 Installation

### Prerequisites
- **Python:** 3.13+ (works with 3.10+)
- **pip:** Latest version
- **Virtual Environment:** Recommended

### Quick Start (5 Minutes)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd tedx_project

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run migrations
python manage.py migrate

# 6. Create superuser (treasurer account)
python manage.py createsuperuser

# 7. (Optional) Load test data
python test_exports.py

# 8. Run development server
python manage.py runserver
```

🎉 **Visit:** `http://127.0.0.1:8000`

### Development Setup (with all tools)

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# This includes:
# - pytest (testing)
# - black (code formatting)
# - flake8 (linting)
# - django-debug-toolbar
# - ipython (better shell)
# - pip-audit (security scanning)
```

---

## 🚀 Key Features

### For Team Members:
- 📝 Submit expenses with receipt uploads
- 📊 View real-time dashboard metrics
- 🔍 Track approval status of submissions
- 📱 Access from any device (mobile-friendly)
- 🔔 Get feedback on rejected transactions

### For Treasurers:
- ✅ Approve/reject transactions with one click
- 💰 Add sponsors with tier classification (Platinum/Gold/Silver/Bronze)
- 💵 Record management fund allocations
- 📈 Set and monitor category budgets
- 📊 Generate comprehensive financial reports
- 📥 Export data to Excel (styled) or PDF (branded)
- ⚡ Bulk operations on multiple transactions
- 📜 View complete audit history
- 📊 Visual analytics dashboard

### For Administrators:
- 👥 Manage user accounts and permissions
- 🔒 Access admin panel for system configuration
- 📊 View system-wide statistics
- 🔍 Monitor all financial activities

---

## 🎯 Technology Stack

### Backend
- **Django 5.2.7** - Web framework with security updates
- **Python 3.13** - Latest stable Python
- **SQLite** - Default database (PostgreSQL for production)
- **django-simple-history** - Audit trail and change tracking
- **django-crispy-forms** - Beautiful form rendering

### Frontend
- **Tailwind CSS** - Utility-first CSS framework (CDN)
- **Chart.js** - Interactive data visualizations
- **Vanilla JavaScript** - No heavy frameworks, fast loading
- **Google Fonts (Inter)** - Modern typography
- **LocalStorage** - Theme persistence

### File Handling
- **openpyxl** - Excel file generation with styling
- **xhtml2pdf** - PDF generation from HTML templates
- **Pillow** - Image processing for uploaded receipts

### Security
- **CSRF Protection** - Built into Django
- **SQL Injection Safe** - Django ORM
- **XSS Protection** - Template auto-escaping
- **File Validation** - Size and type checks
- **Permission System** - Role-based access control

---

## 🤝 User Roles

| Role | Capabilities |
|------|-------------|
| **Admin** | Full system access, user management, system configuration |
| **Treasurer** | Approve/reject transactions, add funds/sponsors, generate reports |
| **Team Member** | Submit expenses, view dashboard, track own submissions |

**Setup:** Assign roles in Django admin panel (`/admin/`)

---

## 📱 Browser Support

| Browser | Supported Versions |
|---------|-------------------|
| Chrome | Latest 2 versions |
| Firefox | Latest 2 versions |
| Safari | Latest 2 versions |
| Edge | Latest 2 versions |
| Mobile Safari | iOS 12+ |
| Mobile Chrome | Android 8+ |

---

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
python manage.py test

# With coverage
pytest --cov=tedx_finance
```

### Test Export Features
```bash
# Create test data and verify exports
python test_exports.py
```

### Security Audit
```bash
# Check for vulnerabilities
pip-audit

# Check Django security
python manage.py check --deploy
```

---

## 🆘 Troubleshooting

### Common Issues

**"No module named 'crispy_forms'"**
```bash
pip install -r requirements.txt
```

**"CSRF verification failed"**
- Ensure `{% csrf_token %}` is in all forms
- Verify cookies are enabled
- Check `CSRF_COOKIE_SECURE` setting

**"Permission denied"**
- Run migrations: `python manage.py migrate`
- Check user permissions in admin panel

**"Static files not loading"**
```bash
python manage.py collectstatic
```

**"Database is locked" (SQLite)**
- Use PostgreSQL for production
- Or increase SQLite timeout in settings

---

## 📈 Scaling Guide

| Users | Recommended Setup |
|-------|-------------------|
| < 10 | SQLite + PythonAnywhere |
| 10-100 | PostgreSQL + Railway/Heroku |
| 100-1000 | DigitalOcean + PostgreSQL + CDN |
| 1000+ | Load balancer + Multiple servers + Redis cache |

---

## 🎉 What Makes This Special

- ✅ **Built for TEDx** - Specifically designed for event finances
- ✅ **Production-Ready** - Security audited, properly tested
- ✅ **Beautiful UI** - Modern glassmorphism design
- ✅ **Fast Setup** - Running in 5 minutes
- ✅ **Comprehensive Docs** - 6 detailed guide documents
- ✅ **Open Source** - MIT License, customize freely
- ✅ **No Subscription** - One-time setup, only hosting costs
- ✅ **Active Development** - Regular updates and improvements

---

## 📊 Project Stats

- **Lines of Code:** ~5000+
- **Templates:** 12 HTML pages
- **Views:** 20+ view functions
- **Models:** 4 core models
- **Security Score:** 98/100
- **Test Coverage:** Ongoing
- **Documentation:** 6 comprehensive guides
- **Dependencies:** 35 core packages

---

## 🗺️ Roadmap

### Completed ✅
- [x] Core financial tracking
- [x] Budget management
- [x] Excel/PDF exports
- [x] Glassmorphic UI
- [x] Dark/light theme
- [x] Audit trail
- [x] Security audit
- [x] Comprehensive documentation

## 🙏 Credits

**Built with ❤️ for TEDx organizers worldwide**

### Special Thanks:
- Django Project for the amazing framework
- Tailwind CSS team for the utility-first CSS
- Chart.js for beautiful visualizations
- All TEDx organizers who provided feedback

---

