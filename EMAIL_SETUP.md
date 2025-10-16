# Email Configuration for Password Reset

## Quick Setup Guide

Password reset functionality requires email configuration. Here are the easiest options:

---

## Option 1: Console Backend (Development/Testing)

**Perfect for**: Testing locally without real emails

Add to `settings.py`:
```python
# For development - prints emails to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Emails will print in your terminal instead of sending. Great for testing!

---

## Option 2: Gmail (Easiest for Production)

**Perfect for**: Small teams, quick setup

### Step 1: Enable App Password
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to App Passwords
4. Generate password for "Mail" app
5. Copy the 16-character password

### Step 2: Configure Django
Add to `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password-here'
DEFAULT_FROM_EMAIL = 'TEDx Finance <your-email@gmail.com>'
```

**Better**: Use environment variables:
```python
import os

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
```

Add to `.env`:
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Gmail Limits:
- Free tier: 500 emails/day
- Paid Google Workspace: 2,000 emails/day

---

## Option 3: SendGrid (Recommended for Production)

**Perfect for**: Professional setup, high volume

### Step 1: Sign Up
1. Go to https://sendgrid.com/
2. Sign up for free (100 emails/day)
3. Verify your email
4. Create API key

### Step 2: Configure Django
```bash
pip install sendgrid-django
```

Add to `settings.py`:
```python
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'
```

### SendGrid Limits:
- Free: 100 emails/day forever
- Essential: $19.95/month - 50,000 emails
- Pro: $89.95/month - 1.5M emails

---

## Option 4: Mailgun

**Perfect for**: Developers, good free tier

### Setup:
1. Sign up at https://www.mailgun.com/
2. Verify domain
3. Get SMTP credentials

```python
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'postmaster@your-domain.mailgun.org'
EMAIL_HOST_PASSWORD = 'your-password'
```

### Mailgun Limits:
- Free: 5,000 emails/month for 3 months
- Foundation: $35/month - 50,000 emails

---

## Option 5: AWS SES (Cheapest for Scale)

**Perfect for**: Large organizations

### Setup:
1. AWS account required
2. Configure SES
3. Verify email/domain
4. Install boto3: `pip install boto3`

```python
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_SES_REGION_NAME = 'us-east-1'
AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'
```

### AWS SES Pricing:
- First 62,000 emails/month: FREE (via EC2)
- After: $0.10 per 1,000 emails

---

## Testing Your Email Configuration

### 1. Django Shell Test
```bash
python manage.py shell
```

```python
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'If you receive this, email is working!',
    'noreply@yourdomain.com',
    ['your-email@example.com'],
    fail_silently=False,
)
```

### 2. Password Reset Test
1. Go to `/accounts/password_reset/`
2. Enter your email
3. Check inbox/console

---

## Recommended Configuration by Stage

### Development (Local)
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
✅ No setup needed  
✅ See emails in terminal

### Staging/Testing
**Option 1**: Gmail with App Password  
**Option 2**: Mailtrap.io (fake SMTP for testing)

```python
EMAIL_HOST = 'smtp.mailtrap.io'
EMAIL_HOST_USER = 'your-username'
EMAIL_HOST_PASSWORD = 'your-password'
EMAIL_PORT = 2525
```

### Production
**Small Team (<100 users)**: Gmail or SendGrid Free  
**Medium Team (100-1000)**: SendGrid Essential  
**Large Organization (1000+)**: AWS SES

---

## Security Best Practices

### 1. Never commit credentials
```python
# ❌ DON'T DO THIS
EMAIL_HOST_PASSWORD = 'mypassword123'

# ✅ DO THIS
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
```

### 2. Use environment variables
Create `.env` file (add to .gitignore):
```
EMAIL_HOST_USER=myemail@gmail.com
EMAIL_HOST_PASSWORD=app-password-here
```

Load in settings.py:
```python
from decouple import config  # pip install python-decouple

EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
```

### 3. Use app passwords (Gmail)
Never use your actual Gmail password!

### 4. Restrict API keys
Set permissions to "mail send" only

---

## Troubleshooting

### "SMTPAuthenticationError"
- Wrong username/password
- Not using app password (for Gmail)
- 2FA not enabled (for Gmail)

### "Connection refused"
- Wrong host/port
- Firewall blocking SMTP (port 587/465)
- Try port 465 with EMAIL_USE_SSL = True

### "Emails not arriving"
- Check spam folder
- Verify sender domain (for SendGrid/Mailgun)
- Check daily limits

### "SSL/TLS errors"
```python
# Try this instead
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
```

---

## Quick Start (Recommended)

For fastest setup:

1. **Development**: Use Console Backend
2. **Production**: Use Gmail with App Password

Total setup time: 5 minutes!

```python
# settings.py
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = 'TEDx Finance <noreply@yourdomain.com>'
```

Done! 🎉

---

## Email Templates Customization

Location: `tedx_finance/templates/registration/`

Files you can customize:
- `password_reset_email.html` - Email body
- `password_reset_subject.txt` - Email subject

Example custom email:
```html
Hi {{ user.username }},

You requested a password reset for your TEDx Finance Hub account.

Click here to reset: {{ protocol }}://{{ domain }}{% url 'password_reset_confirm' uidb64=uid token=token %}

This link expires in 24 hours.

If you didn't request this, ignore this email.

Best,
TEDx Finance Team
```

---

**Need help?** Check Django email docs: https://docs.djangoproject.com/en/4.2/topics/email/
