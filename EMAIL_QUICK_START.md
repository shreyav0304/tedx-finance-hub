# 🚀 EMAIL SYSTEM - QUICK START

## Already Works (No Setup Needed!)

### Development Mode
Emails print to console automatically. Just run the server:
```bash
python manage.py runserver
```

### What's Automatically Done
- ✅ Email verification on signup (24-hour token)
- ✅ Login notification emails (with IP, browser, time)
- ✅ Password reset emails (24-hour reset link)
- ✅ User preference to toggle notifications
- ✅ Rate limiting on login attempts
- ✅ Error handling (email failures don't break login)

---

## For Production: Choose ONE Provider

### Option 1: Gmail (Easiest) ⭐
1. Go to: https://myaccount.google.com/apppasswords
2. Generate app password
3. Add to environment:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=16-char-password-here
```

### Option 2: SendGrid (Recommended) 🏆
1. Sign up: https://sendgrid.com
2. Get API key from dashboard
3. Add to environment:
```
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=SG.xxx
```
Install: `pip install sendgrid-django`

### Option 3: AWS SES
1. Set up AWS SES
2. Get access keys
3. Add to environment (see EMAIL_SETUP_GUIDE.md)
Install: `pip install django-ses`

---

## Test It Works

### Step 1: Local Testing
1. Start server: `python manage.py runserver`
2. Go to: http://localhost:8000/signup
3. Create account
4. Check console - you'll see verification email
5. Copy verification URL and visit it
6. Log in - check console for login notification

### Step 2: Production Testing
1. Set EMAIL_HOST, EMAIL_PORT, etc. in environment variables
2. Deploy code
3. Sign up with real email at yoursite.com/signup
4. Check inbox for verification email
5. Click verification link
6. Log in - check inbox for login notification

---

## Email Notification Types

| Type | Sent To | When | Required |
|------|---------|------|----------|
| Verification | New users | After signup | Yes |
| Login Notification | Logged-in users | Every login* | No (toggle in Settings) |
| Password Reset | Users | On reset request | Yes |

*Can be disabled in user Settings page

---

## Environment Variables Template

```bash
# Development (optional - uses console by default)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Production
DJANGO_DEBUG=false
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-email@provider.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

---

## Files You Might Need

| File | Purpose |
|------|---------|
| `EMAIL_SETUP_GUIDE.md` | Complete detailed guide |
| `EMAIL_CONFIGURATION.md` | Provider-specific setup |
| `EMAIL_VERIFICATION_COMPLETE.md` | Full implementation details |
| `.env.production.example` | Example environment variables |

---

## Troubleshooting

**"Email not sending"**
→ Check: Is EMAIL_BACKEND set to smtp.EmailBackend in production?

**"SMTPAuthenticationError"**
→ For Gmail: Use App Password, not regular password

**"ConnectionRefused"**
→ Check: EMAIL_HOST and EMAIL_PORT are correct

**"Email sends to console instead of inbox"**
→ Check: DJANGO_DEBUG=false in production

---

## That's It! 🎉

The email system is already built and working. Just:
1. Choose a provider
2. Get credentials
3. Set environment variables
4. Deploy!

No code changes needed. Everything is ready to go.

For details, see `EMAIL_SETUP_GUIDE.md`
