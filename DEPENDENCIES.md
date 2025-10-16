# 📦 Dependency Management Guide

## Overview
This document explains the dependency management strategy for the TEDx Finance Hub project.

---

## 📋 Requirements Files

### 1. `requirements.txt` (Base Dependencies)
**Purpose:** Core dependencies required to run the application  
**When to use:** Development, testing, and production  
**Install:** `pip install -r requirements.txt`

**Categories:**
- ✅ Django framework and core dependencies
- ✅ Form handling and UI (crispy-forms, crispy-tailwind)
- ✅ History tracking (django-simple-history)
- ✅ File handling (openpyxl for Excel)
- ✅ PDF generation (xhtml2pdf and dependencies)
- ✅ Security and cryptography libraries

### 2. `requirements-dev.txt` (Development Dependencies)
**Purpose:** Additional tools for development, testing, and debugging  
**When to use:** Local development only  
**Install:** `pip install -r requirements-dev.txt`

**Categories:**
- 🧪 Testing frameworks (pytest, coverage)
- 🔍 Code quality tools (black, flake8, pylint)
- 🐛 Debugging tools (django-debug-toolbar, ipython)
- 📚 Documentation generators (Sphinx)
- 🔒 Security scanners (bandit, safety)

### 3. `requirements-prod.txt` (Production Dependencies)
**Purpose:** Additional packages needed for production deployment  
**When to use:** Production environment only  
**Install:** `pip install -r requirements-prod.txt`

**Categories:**
- 🗄️ Database adapters (psycopg2 for PostgreSQL)
- 🚀 WSGI servers (gunicorn)
- 📁 Static file serving (whitenoise)
- 📊 Monitoring (sentry-sdk)
- 📧 Email backends (django-anymail)
- ⚡ Caching (redis, django-redis)
- 📋 Task queues (celery)

---

## 🚀 Quick Start

### Local Development Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install base dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### Production Deployment
```bash
# Install production dependencies
pip install -r requirements-prod.txt
```

---

## 🔄 Updating Dependencies

### Check for Outdated Packages
```bash
pip list --outdated
```

### Update All Packages (Carefully!)
```bash
# Generate current versions
pip freeze > requirements-current.txt

# Update all packages
pip install --upgrade -r requirements.txt

# Test thoroughly!
python manage.py test

# If issues occur, rollback:
pip install -r requirements-current.txt
```

### Update Specific Package
```bash
# Update Django to latest 5.2.x
pip install --upgrade "Django>=5.2,<5.3"

# Update and save to requirements
pip freeze | grep Django > temp.txt
# Manually update requirements.txt with new version
```

---

## 🔒 Security Best Practices

### 1. Regular Security Audits
```bash
# Install security tools
pip install pip-audit safety

# Check for vulnerabilities
pip-audit
safety check

# Or using bandit for code security
bandit -r tedx_finance/
```

### 2. Pin All Versions
✅ **Good:** `Django==5.2.1`  
❌ **Bad:** `Django` or `Django>=5.2`

**Why?** Ensures reproducible builds and prevents unexpected updates.

### 3. Review Dependencies
Before adding new packages:
1. ✅ Check package reputation and maintenance
2. ✅ Review security advisories
3. ✅ Check license compatibility
4. ✅ Verify actual need (avoid bloat)

### 4. Update Regularly
```bash
# Monthly security update schedule
# 1. Check for security advisories
# 2. Update vulnerable packages
# 3. Test thoroughly
# 4. Deploy to production
```

---

## 📊 Dependency Analysis

### Current Package Count
```bash
# Base dependencies: ~35 packages
# Development add-ons: ~25 packages
# Production add-ons: ~20 packages
```

### Size Considerations
```bash
# Check installed package sizes
pip list --format=freeze | xargs pip show | grep -E '^(Name|Size)' | grep -B1 Size
```

---

## 🛠️ Troubleshooting

### Issue 1: Conflicting Dependencies
**Symptom:** `pip install` fails with dependency conflict  
**Solution:**
```bash
# Check conflicts
pip check

# Use pip's dependency resolver
pip install --use-feature=fast-deps -r requirements.txt

# Or create fresh environment
rm -rf venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue 2: Missing System Dependencies
**Symptom:** Build errors during `pip install`  
**Common Causes:**
- `Pillow`: Missing image libraries
- `lxml`: Missing libxml2/libxslt
- `pycairo`: Missing Cairo graphics library
- `psycopg2`: Missing PostgreSQL development headers

**Solutions:**
```bash
# Windows: Use binary wheels (usually automatic)
pip install psycopg2-binary

# Ubuntu/Debian:
sudo apt-get install python3-dev libpq-dev libxml2-dev libxslt1-dev

# macOS:
brew install postgresql libxml2 cairo
```

### Issue 3: Import Errors After Install
**Symptom:** `ModuleNotFoundError` despite package being installed  
**Solution:**
```bash
# Verify installation
pip show package-name

# Check virtual environment is activated
which python  # Should point to venv

# Reinstall package
pip uninstall package-name
pip install package-name
```

---

## 📦 Package Details

### Core Dependencies

#### Django (5.2.1)
- **Purpose:** Web framework
- **Size:** ~8 MB
- **Security:** Update regularly, follow Django security releases
- **Docs:** https://docs.djangoproject.com/

#### openpyxl (3.1.5)
- **Purpose:** Excel file handling
- **Size:** ~2 MB
- **Used in:** Export/import transactions
- **Alternative:** xlsxwriter (write-only, faster)

#### xhtml2pdf (0.2.17)
- **Purpose:** PDF generation from HTML
- **Size:** ~400 KB + dependencies (~15 MB total)
- **Used in:** Finance report PDF export
- **Alternative:** WeasyPrint (better CSS support)

#### django-simple-history (3.10.1)
- **Purpose:** Model change tracking
- **Size:** ~200 KB
- **Used in:** Audit trail for transactions
- **Overhead:** Creates additional database tables

#### django-crispy-forms (2.4) + crispy-tailwind (1.0.3)
- **Purpose:** Better form rendering with Tailwind CSS
- **Size:** ~500 KB total
- **Used in:** All forms (transaction, sponsor, fund)

---

## 🔄 Version Compatibility Matrix

| Package | Min Version | Max Version | Python | Django |
|---------|-------------|-------------|--------|--------|
| Django | 5.2.0 | 5.2.x | 3.10+ | - |
| django-crispy-forms | 2.0 | 2.x | 3.8+ | 4.2+ |
| crispy-tailwind | 1.0 | 1.x | 3.8+ | 4.2+ |
| django-simple-history | 3.0 | 3.x | 3.8+ | 4.2+ |
| openpyxl | 3.0 | 3.x | 3.7+ | - |
| xhtml2pdf | 0.2 | 0.2.x | 3.7+ | - |

---

## 🎯 Optimization Tips

### 1. Use Binary Wheels
```bash
# Prefer binary packages for faster installs
pip install --only-binary :all: package-name
```

### 2. Leverage Caching
```bash
# Use pip cache
pip install --cache-dir ~/.cache/pip -r requirements.txt

# Or use pipenv/poetry for better dependency resolution
```

### 3. Minimize Dependencies
```bash
# Find unused dependencies
pip install pipdeptree
pipdeptree --reverse

# Remove unused packages
pip uninstall package-name
```

### 4. Use Virtual Environments
```bash
# Always use virtual environments
# Never install globally
python -m venv venv
```

---

## 📝 Maintenance Checklist

### Monthly Tasks
- [ ] Check for security advisories
- [ ] Run `pip list --outdated`
- [ ] Update critical security patches
- [ ] Test application after updates
- [ ] Update requirements files

### Quarterly Tasks
- [ ] Major version updates review
- [ ] Dependency audit (remove unused)
- [ ] Performance benchmarking
- [ ] Documentation updates

### Before Each Deployment
- [ ] Freeze exact versions: `pip freeze > deployed-versions.txt`
- [ ] Run security audit: `pip-audit`
- [ ] Run tests: `python manage.py test`
- [ ] Check for deprecated features

---

## 🔗 Useful Commands

```bash
# List installed packages
pip list

# Show package details
pip show package-name

# Check dependencies
pip check

# Generate requirements
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt

# Uninstall all packages
pip freeze | xargs pip uninstall -y

# Search for package
pip search package-name  # (deprecated, use PyPI website)

# Show dependency tree
pip install pipdeptree
pipdeptree

# Check for security issues
pip install pip-audit
pip-audit
```

---

## 📚 Additional Resources

- **PyPI (Python Package Index):** https://pypi.org/
- **Django Packages:** https://djangopackages.org/
- **Snyk Vulnerability Database:** https://snyk.io/vuln/
- **Safety DB:** https://github.com/pyupio/safety-db
- **Django Security:** https://docs.djangoproject.com/en/stable/topics/security/

---

## 🆘 Getting Help

1. **Check documentation:** Read package docs on PyPI
2. **Search issues:** GitHub issues for the package
3. **Stack Overflow:** Search existing questions
4. **Django Forums:** https://forum.djangoproject.com/
5. **Discord/Slack:** Django community channels

---

**Last Updated:** October 15, 2025  
**Maintainer:** TEDx Finance Hub Team  
**Review Schedule:** Monthly
