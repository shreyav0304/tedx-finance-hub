# DEPLOYMENT GUIDE: Railway.app (Recommended)

## Why Railway?
- ✅ FREE tier with 500MB PostgreSQL
- ✅ Automatic HTTPS
- ✅ GitHub integration
- ✅ Zero config needed
- ✅ Scales automatically

## Step-by-Step Deployment

### 1. Prepare Your Project

Add these files (already done if you have them):

**`runtime.txt`**
```
python-3.11
```

**`Procfile`**
```
web: gunicorn realtime_tedx.wsgi --log-file -
```

**Update `requirements.txt`** - add:
```
gunicorn
psycopg2-binary
dj-database-url
whitenoise
```

### 2. Update Django Settings

Add to `settings.py`:

```python
import os
import dj_database_url

# Production settings
if not DEBUG:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL')
        )
    }
    
    # Static files
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # Security
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

### 3. Deploy to Railway

#### Option A: Using Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Add PostgreSQL
railway add postgresql

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser
```

#### Option B: Using GitHub

1. Push code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/tedx-finance.git
   git push -u origin main
   ```

2. Go to https://railway.app
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository
6. Add PostgreSQL plugin
7. Set environment variables:
   - `SECRET_KEY` = (generate new one)
   - `DEBUG` = False
   - `ALLOWED_HOSTS` = your-app.railway.app

8. Deploy!

### 4. Post-Deployment

```bash
# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Collect static files
railway run python manage.py collectstatic --noinput
```

### 5. Custom Domain (Optional)

1. In Railway dashboard, go to Settings
2. Add your domain
3. Update DNS records:
   ```
   Type: CNAME
   Name: tedx-finance (or @)
   Value: your-app.railway.app
   ```

## Environment Variables to Set:

```
SECRET_KEY=your-new-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app.railway.app,yourdomain.com
DATABASE_URL=(automatically set by Railway)
```

## Troubleshooting

**"Application failed to respond"**
- Check logs: `railway logs`
- Verify Procfile is correct
- Ensure gunicorn is in requirements.txt

**"Static files not loading"**
- Run: `railway run python manage.py collectstatic`
- Check STATIC_ROOT in settings

**"Database errors"**
- Verify DATABASE_URL is set
- Run migrations: `railway run python manage.py migrate`

## Monitoring

View logs:
```bash
railway logs
```

Check database:
```bash
railway run python manage.py dbshell
```

## Backup

Railway automatically backs up PostgreSQL!

Manual backup:
```bash
railway run pg_dump DATABASE_URL > backup.sql
```

## Cost

- **Free Tier**: $5 credit/month (enough for small team)
- **Hobby Plan**: $5/month (more resources)
- **Pro Plan**: $20/month (production apps)

## What's Included

✅ PostgreSQL database (500MB free)
✅ Automatic SSL certificates
✅ CI/CD from GitHub
✅ Environment variable management
✅ Automatic backups
✅ Monitoring & logs

---

# Alternative: PythonAnywhere (Easiest)

## For Non-Technical Users

1. Go to https://www.pythonanywhere.com
2. Sign up (free account)
3. Upload your code via "Files" tab
4. Create virtual environment:
   ```bash
   mkvirtualenv myenv --python=python3.11
   pip install -r requirements.txt
   ```
5. Configure Web app:
   - Source code: `/home/yourusername/tedx_project`
   - Virtual env: `/home/yourusername/.virtualenvs/myenv`
   - WSGI: Edit to point to your app
6. Reload web app

**Cost**: Free (yourusername.pythonanywhere.com)
**Upgrade**: $5/month for custom domain

---

# Self-Hosted (VPS) - Advanced

## For Full Control

```bash
# 1. Set up server (Ubuntu 22.04)
ssh root@your-server-ip

# 2. Install dependencies
apt update
apt install python3 python3-pip python3-venv nginx postgresql

# 3. Create database
sudo -u postgres createdb tedx_finance
sudo -u postgres createuser tedx_user -P

# 4. Clone and setup
cd /var/www
git clone your-repo
cd tedx_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn

# 5. Configure environment
cp .env.example .env
nano .env  # Edit values

# 6. Run migrations
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser

# 7. Configure Gunicorn
sudo nano /etc/systemd/system/gunicorn.service

# 8. Configure Nginx
sudo nano /etc/nginx/sites-available/tedx_finance

# 9. Start services
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl restart nginx
```

**Cost**: $5-10/month (VPS)
**Pros**: Full control
**Cons**: You manage everything

---

## Quick Comparison

| Platform | Difficulty | Cost/Month | Database | SSL | Backup |
|----------|-----------|------------|----------|-----|--------|
| Railway | Easy | $0-5 | PostgreSQL | Auto | Auto |
| PythonAnywhere | Easiest | $0-5 | SQLite/MySQL | Auto | Manual |
| Heroku | Easy | $7+ | PostgreSQL | Auto | Add-on |
| VPS | Hard | $5-10 | Your choice | Manual | Manual |

**Recommendation**: Start with Railway, it's the best balance!
