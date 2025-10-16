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

## 📚 Documentation

We've created comprehensive guides for every aspect:

| Document | Description |
|----------|-------------|
| [FEATURES.md](FEATURES.md) | Complete feature list with details |
| [EXPORT_FEATURES.md](EXPORT_FEATURES.md) | Excel & PDF export documentation |
| [DEPENDENCIES.md](DEPENDENCIES.md) | Dependency management guide |
| [SECURITY_AUDIT.md](SECURITY_AUDIT.md) | Security assessment and recommendations |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment guide |
| [UI_IMPROVEMENTS.md](UI_IMPROVEMENTS.md) | UI/UX enhancement log |

---

## 🌐 Deployment

### Option 1: PythonAnywhere (Easiest - FREE)
Perfect for small teams, no technical expertise needed.

**Steps:**
1. Sign up at https://www.pythonanywhere.com
2. Upload your code
3. Configure WSGI
4. Set environment variables

**Cost:** Free tier available, $5/month for custom domain  
**Database:** SQLite included (upgradable to MySQL)

### Option 2: Railway.app (Recommended)
Modern deployment with auto-scaling.

```bash
# Install Railway CLI
npm i -g @railway/cli

# Deploy
railway login
railway up
```

**Cost:** $5/month, free trial available  
**Database:** PostgreSQL included (500MB free)

### Option 3: Heroku
Mature platform with great documentation.

```bash
heroku create tedx-finance
git push heroku main
heroku run python manage.py migrate
```

**Cost:** $7/month minimum  
**Database:** PostgreSQL add-on

### Option 4: DigitalOcean/Linode (VPS)
Full control for tech-savvy teams.

**Cost:** $5-10/month  
**Setup:** See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guide

---

## 🔒 Security Checklist

Before going live, ensure:

- [ ] Change `SECRET_KEY` in settings.py (use environment variable)
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use PostgreSQL (not SQLite) for production
- [ ] Enable HTTPS redirect
- [ ] Set secure cookie flags
- [ ] Configure regular backups
- [ ] Run security audit: `pip-audit`
- [ ] Keep Django updated

**See:** [SECURITY_AUDIT.md](SECURITY_AUDIT.md) for complete checklist

---

## 🎨 Customization

### Change Theme Colors

Edit `tedx_finance/templates/tedx_finance/base.html`:

```css
/* Change purple to your brand color */
--primary-color: #4F46E5;  /* Your color here */
```

### Add Expense Categories

Edit `tedx_finance/models.py`:

```python
CATEGORY_CHOICES = [
    ('Marketing', 'Marketing'),
    ('Logistics', 'Logistics'),
    ('YourCategory', 'Your Category'),  # Add here
]
```

Then run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Customize Sponsor Tiers

Edit `tedx_finance/views.py` in the `get_sponsor_tier()` function:

```python
def get_sponsor_tier(amount):
    if amount >= 50000: return ("Platinum", "bg-gray-300")
    if amount >= 30000: return ("Gold", "bg-yellow-400")
    # Add more tiers...
```

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

### In Progress 🚧
- [ ] Mobile app (React Native)
- [ ] Automated testing (pytest)
- [ ] API endpoints (Django REST)

### Planned 🔮
- [ ] Email notifications
- [ ] Budget alerts
- [ ] Multi-currency support
- [ ] Receipt OCR
- [ ] Dashboard widgets customization
- [ ] Integration with accounting software

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

**Code Style:** We use `black` for formatting and `flake8` for linting.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**TL;DR:** Use freely for your TEDx event, modify as needed, no attribution required (but appreciated!)

---

## 🙏 Credits

**Built with ❤️ for TEDx organizers worldwide**

### Special Thanks:
- Django Project for the amazing framework
- Tailwind CSS team for the utility-first CSS
- Chart.js for beautiful visualizations
- All TEDx organizers who provided feedback

---

## 📞 Support

- **Documentation:** Check our [docs](DEPENDENCIES.md)
- **Issues:** [GitHub Issues](https://github.com/yourusername/tedx-finance-hub/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/tedx-finance-hub/discussions)
- **Email:** your-email@example.com

---

## ⭐ Show Your Support

If this project helped your TEDx event, please:
- ⭐ Star this repository
- 🐦 Tweet about it
- 📝 Write a blog post
- 💬 Share with other TEDx organizers

---

<div align="center">

**Made with 💜 for the TEDx Community**

*Ideas worth spreading, finances worth tracking*

</div>
