# ============================================
# EMAIL CONFIGURATION GUIDE
# ============================================
# This file shows how to configure email for production deployment

# ============================================
# GMAIL SMTP CONFIGURATION (Recommended for testing/small deployments)
# ============================================
# 1. Enable 2-Factor Authentication on your Gmail account
# 2. Generate an App Password (not your regular password):
#    - Go to https://myaccount.google.com/apppasswords
#    - Select "Mail" and "Windows Computer" (or your device)
#    - Generate the password
# 3. Use these environment variables:

# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=true
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
# DEFAULT_FROM_EMAIL=TEDx Finance <noreply@tedxfinancehub.com>

# ============================================
# SENDGRID CONFIGURATION (Production recommended)
# ============================================
# 1. Sign up at https://sendgrid.com
# 2. Get your API key from SendGrid dashboard
# 3. Use these environment variables:

# EMAIL_BACKEND=sendgrid_backend.SendgridBackend
# SENDGRID_API_KEY=SG.your-api-key
# DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Install sendgrid package:
# pip install sendgrid-django

# ============================================
# AWS SES CONFIGURATION
# ============================================
# 1. Set up AWS SES in your region
# 2. Verify your email address/domain
# 3. Use these environment variables:

# EMAIL_BACKEND=django_ses.SESBackend
# AWS_SES_REGION_NAME=us-east-1
# AWS_SES_REGION_ENDPOINT=email.us-east-1.amazonaws.com
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key
# DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Install aws-ses package:
# pip install django-ses

# ============================================
# EMAIL CONFIGURATION FOR LOCAL DEVELOPMENT
# ============================================
# In development, the system uses console backend which prints emails to console
# No configuration needed - just run the server and check the console output

# ============================================
# ENVIRONMENT VARIABLES NEEDED
# ============================================
# Required for production:
# - DJANGO_DEBUG=false
# - EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# - EMAIL_HOST=smtp.gmail.com (or your SMTP provider)
# - EMAIL_PORT=587
# - EMAIL_USE_TLS=true
# - EMAIL_HOST_USER=your-email@provider.com
# - EMAIL_HOST_PASSWORD=your-app-password
# - DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# ============================================
# WHICH EMAIL ADDRESSES GET NOTIFICATIONS?
# ============================================
# 1. EMAIL VERIFICATION: Sent to all new users during registration
#    - Verifies email address
#    - Creates temporary verification token (24-hour validity)
#    - User must verify before login

# 2. LOGIN NOTIFICATIONS: Sent on every successful login
#    - Shows login time, browser, IP address
#    - Only sent if user has email_notifications enabled in preferences
#    - Helps user detect suspicious logins

# 3. PASSWORD RESET: Sent when user requests password reset
#    - Contains secure password reset link
#    - Link expires after 24 hours
#    - Only user can click the link to reset

# ============================================
# TESTING EMAIL DELIVERY
# ============================================
# 1. Sign up for an account at http://localhost:8000/signup
# 2. Check your console output - you'll see the verification email
# 3. Copy the verification token from the email
# 4. Visit: http://localhost:8000/verify-email/{token}/
# 5. You should see success message

# For production:
# 1. Configure EMAIL_BACKEND to SMTP
# 2. Sign up for account
# 3. Check your email inbox
# 4. Click verification link
# 5. Login with your credentials
# 6. Check email for login notification

# ============================================
# TROUBLESHOOTING
# ============================================
# Issue: "SMTPAuthenticationError"
# Solution: Check that EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are correct
#          For Gmail, ensure you're using App Password, not account password

# Issue: "SMTPNotSupportedError"
# Solution: Ensure EMAIL_USE_TLS is set to true for port 587

# Issue: "ConnectionRefusedError"
# Solution: Check that EMAIL_HOST and EMAIL_PORT are correct

# Issue: Emails not being sent
# Solution: Set EMAIL_BACKEND to console backend in DEBUG mode
#         Check that DEFAULT_FROM_EMAIL is set correctly
#         Ensure user has email address in database
