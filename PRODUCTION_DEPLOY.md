# 🚀 Production Deployment Checklist

**Last Updated**: October 22, 2025  
**Project**: TEDx Finance Hub  
**Status**: Ready for Production Deployment

---

## 📋 Pre-Deployment Checklist

### 1. ✅ Environment Configuration

#### Generate Production SECRET_KEY
```bash
# Generate a new secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Set as environment variable (do NOT commit to Git)
export DJANGO_SECRET_KEY='your-generated-secret-key-here'
```

#### Set Required Environment Variables
```bash
# Core Settings
export DJANGO_SECRET_KEY='your-new-secret-key-from-above'
export DJANGO_DEBUG='False'
export DJANGO_ALLOWED_HOSTS='yourdomain.com,www.yourdomain.com'

# Database (PostgreSQL recommended for production)
export DATABASE_URL='postgresql://user:password@host:5432/dbname'

# Security Settings (auto-enabled when DEBUG=False)
export DJANGO_SECURE_SSL_REDIRECT='True'
export DJANGO_SECURE_HSTS_SECONDS='31536000'
export DJANGO_CSRF_TRUSTED_ORIGINS='https://yourdomain.com'

# Email (optional - for notifications)
export EMAIL_HOST='smtp.gmail.com'
export EMAIL_PORT='587'
export EMAIL_USE_TLS='True'
export EMAIL_HOST_USER='your-email@gmail.com'
export EMAIL_HOST_PASSWORD='your-app-password'
```

---

### 2. ✅ Security Verification

Run the deployment check:
```bash
python manage.py check --deploy
```

**Expected Result**: No errors, only informational messages.

**Common Warnings to Address**:
- ✅ `SECRET_KEY` - Must be changed from default
- ✅ `DEBUG` - Must be False in production
- ✅ `ALLOWED_HOSTS` - Must include your domain
- ✅ SSL/HTTPS - Configure on your hosting platform

---

### 3. ✅ Database Migration

#### Switch to PostgreSQL (Recommended)
```bash
# Install PostgreSQL adapter
pip install psycopg2-binary

# Set DATABASE_URL environment variable
export DATABASE_URL='postgresql://user:password@host:5432/dbname'

# Run migrations
python manage.py migrate

# Create superuser (treasurer)
python manage.py createsuperuser
```

#### Import Existing Data (if migrating from SQLite)
```bash
# Export from SQLite
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > data.json

# Load into PostgreSQL
python manage.py loaddata data.json
```

---

### 4. ✅ Static Files Setup

```bash
# Collect all static files
python manage.py collectstatic --noinput

# Verify STATIC_ROOT is set correctly
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise is already configured for static file serving
# No additional CDN setup needed unless serving 1000+ users
```

---

### 5. ✅ Media Files Configuration

For file uploads (receipts, agreements):

**Option A: Local Storage (Simple)**
```python
# settings.py (already configured)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

**Option B: Cloud Storage (Scalable)**
```bash
# AWS S3 Example
pip install django-storages boto3

# Set environment variables
export AWS_ACCESS_KEY_ID='your-key'
export AWS_SECRET_ACCESS_KEY='your-secret'
export AWS_STORAGE_BUCKET_NAME='your-bucket'
export AWS_S3_REGION_NAME='us-east-1'
```

---

## 🌐 Deployment Platforms

### Option 1: Railway (Recommended - Easiest)

1. **Sign up**: https://railway.app
2. **Create New Project** → Deploy from GitHub
3. **Configure Variables**:
   ```
   DJANGO_SECRET_KEY=<generated-key>
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}}
   DATABASE_URL=${{DATABASE_URL}}  # Auto-provided by Railway
   ```
4. **Deploy**: Railway auto-deploys on git push

**Cost**: Free tier → $5/month (sufficient for 100+ users)

---

### Option 2: PythonAnywhere

1. **Sign up**: https://www.pythonanywhere.com
2. **Upload code** via Git or file manager
3. **Configure Web App**:
   - Python version: 3.10+
   - WSGI file: `/path/to/realtime_tedx/wsgi.py`
4. **Set environment variables** in WSGI file:
   ```python
   import os
   os.environ['DJANGO_SECRET_KEY'] = 'your-key'
   os.environ['DJANGO_DEBUG'] = 'False'
   ```
5. **Run migrations**: Via console
6. **Reload web app**

**Cost**: Free tier → $5/month

---

### Option 3: Heroku

1. **Install Heroku CLI**
2. **Create app**: `heroku create tedx-finance-hub`
3. **Add PostgreSQL**: `heroku addons:create heroku-postgresql:mini`
4. **Set config vars**:
   ```bash
   heroku config:set DJANGO_SECRET_KEY='your-key'
   heroku config:set DJANGO_DEBUG='False'
   heroku config:set DJANGO_ALLOWED_HOSTS='your-app.herokuapp.com'
   ```
5. **Deploy**:
   ```bash
   git push heroku main
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

**Cost**: $5-7/month (Eco Dynos)

---

### Option 4: DigitalOcean App Platform

1. **Connect GitHub repository**
2. **Configure build settings**:
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Run Command: `gunicorn realtime_tedx.wsgi:application`
3. **Add PostgreSQL database** ($15/month)
4. **Set environment variables** in dashboard
5. **Deploy**

**Cost**: $12/month (app) + $15/month (database) = $27/month

---

## 🔒 Security Post-Deployment

### Immediate Actions

1. **Change Default SECRET_KEY**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Enable HTTPS** (Most platforms auto-enable):
   - Railway: Automatic
   - PythonAnywhere: Automatic
   - Heroku: Automatic
   - DigitalOcean: Enable in settings

3. **Set CSRF Trusted Origins**
   ```python
   CSRF_TRUSTED_ORIGINS = ['https://yourdomain.com']
   ```

4. **Create Initial Treasurer Account**
   ```bash
   python manage.py createsuperuser
   # Add user to "Treasurer" group in Django admin
   ```

5. **Verify Security Settings**
   ```bash
   python manage.py check --deploy
   ```

---

## 📊 Monitoring & Maintenance

### Setup Error Tracking (Optional but Recommended)

**Sentry.io Integration**:
```bash
pip install sentry-sdk

# Add to settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
)
```

### Regular Maintenance

- [ ] **Weekly**: Check error logs
- [ ] **Monthly**: Update dependencies (`pip list --outdated`)
- [ ] **Quarterly**: Security audit (`pip-audit`)
- [ ] **As needed**: Database backups (most platforms auto-backup)

---

## 🧪 Testing Production Setup

### Pre-Launch Checklist

1. **Test Authentication**
   - [ ] Login works
   - [ ] Logout works
   - [ ] Password reset works (if email configured)

2. **Test Core Features**
   - [ ] Add transaction (with file upload)
   - [ ] Approve transaction (as treasurer)
   - [ ] Add sponsor
   - [ ] View dashboard charts
   - [ ] Export to Excel
   - [ ] Export to PDF
   - [ ] View proof gallery

3. **Test Security**
   - [ ] Non-treasurer cannot approve transactions
   - [ ] CSRF protection enabled on forms
   - [ ] File upload size limits working (5MB)
   - [ ] HTTPS enforced (no HTTP access)

4. **Test Performance**
   - [ ] Page loads < 2 seconds
   - [ ] Charts render correctly
   - [ ] Large transaction lists load quickly

---

## 🐛 Troubleshooting Common Issues

### Issue: Static Files Not Loading

**Solution**:
```bash
python manage.py collectstatic --clear --noinput
# Verify STATIC_ROOT path is correct
```

### Issue: Database Connection Errors

**Solution**:
```bash
# Verify DATABASE_URL format
# PostgreSQL: postgresql://user:pass@host:5432/dbname
# Check database credentials
# Ensure database service is running
```

### Issue: 500 Internal Server Error

**Solution**:
```bash
# Check logs (platform-specific):
# Railway: Dashboard → Logs
# Heroku: heroku logs --tail
# PythonAnywhere: Error log file

# Common causes:
# - DEBUG=True in production (set to False)
# - Missing environment variables
# - Database migration not run
```

### Issue: CSRF Verification Failed

**Solution**:
```python
# Add to settings.py
CSRF_TRUSTED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
]
```

---

## 📈 Scaling Considerations

### For 10-100 Users (Current Setup)
- ✅ SQLite or PostgreSQL
- ✅ Single server
- ✅ WhiteNoise for static files
- ✅ Railway/PythonAnywhere

### For 100-1000 Users
- ⬆️ PostgreSQL required
- ⬆️ Redis caching
- ⬆️ CDN for static files (Cloudflare)
- ⬆️ DigitalOcean or AWS

### For 1000+ Users
- ⬆️ Load balancer
- ⬆️ Multiple app servers
- ⬆️ S3 for media files
- ⬆️ Managed database (RDS)
- ⬆️ Full CDN integration

---

## ✅ Final Deployment Steps

1. [ ] **Generate and set SECRET_KEY**
2. [ ] **Set DEBUG=False**
3. [ ] **Configure ALLOWED_HOSTS**
4. [ ] **Set up PostgreSQL database**
5. [ ] **Run migrations**
6. [ ] **Collect static files**
7. [ ] **Create superuser/treasurer**
8. [ ] **Run deployment check**
9. [ ] **Deploy to platform**
10. [ ] **Test all features**
11. [ ] **Enable HTTPS**
12. [ ] **Set up monitoring**
13. [ ] **Document deployment for team**

---

## 📞 Support Resources

- **Django Deployment Docs**: https://docs.djangoproject.com/en/5.0/howto/deployment/
- **Django Security Checklist**: https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
- **Railway Docs**: https://docs.railway.app/
- **PythonAnywhere Help**: https://help.pythonanywhere.com/
- **Heroku Django Guide**: https://devcenter.heroku.com/articles/django-app-configuration

---

## 🎉 Post-Deployment

**Congratulations! Your TEDx Finance Hub is now live! 🚀**

### Share with Your Team

1. Provide login URL
2. Create treasurer accounts
3. Import existing data (if any)
4. Train 2-3 power users
5. Run parallel with Excel for 1 week
6. Collect feedback
7. Full rollout!

---

*Last Updated: October 22, 2025*  
*Version: 1.0.0*  
*Project: TEDx Finance Hub*
