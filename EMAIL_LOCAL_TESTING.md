# 🧪 EMAIL SYSTEM - LOCAL TESTING GUIDE

## Quick Start

### Step 1: Server Already Running
✅ Django development server is running at http://localhost:8000

### Step 2: Create Test Account
1. Go to http://localhost:8000/signup
2. Fill in the form:
   - **Username**: testuser123
   - **Email**: test@example.com
   - **Password**: TestPass123!
   - **Confirm Password**: TestPass123!
3. Click "Sign Up"

### Step 3: Check Console for Verification Email
Look at the Django server console output. You'll see something like:

```
Content-Type: text/html; charset="utf-8"
MIME-Version: 1.0
Subject: Verify your TEDx Finance Hub email

[EMAIL CONTENT HERE]
```

Look for the verification URL in the console output.

### Step 4: Verify Email
Copy the verification URL from console and visit it in your browser:
```
http://localhost:8000/verify-email/TOKEN_HERE/
```

### Step 5: Login
1. Go to http://localhost:8000/login
2. Enter credentials:
   - **Username**: testuser123
   - **Password**: TestPass123!
3. Click Login

Check the Django console again - you should see the login notification email printed!

### Step 6: Password Reset (Optional)
1. Go to http://localhost:8000/login
2. Click "Forgot your password?"
3. Enter email: test@example.com
4. Check console for password reset email
5. Copy reset link from console
6. Visit the link and set new password

---

## What You'll See in Console

### Verification Email
```
Content-Type: text/html; charset="utf-8"
MIME-Version: 1.0
Subject: Verify your TEDx Finance Hub email
To: test@example.com
From: noreply@tedxfinancehub.com

<!DOCTYPE html>
<html>
...
[Professional HTML email here]
...
</html>

───────────────────────────────────────────────
```

### Login Notification Email
```
Content-Type: text/html; charset="utf-8"
MIME-Version: 1.0
Subject: New Login to Your TEDx Finance Hub Account
To: test@example.com
From: noreply@tedxfinancehub.com

<!DOCTYPE html>
<html>
...
[Professional HTML email with login details]
...
</html>

───────────────────────────────────────────────
```

---

## Email Template Features

### ✨ Verification Email Includes:
- Welcome message
- One-click verification button
- Fallback URL (copy-paste)
- 24-hour expiration warning
- Why verify section
- Support contact info
- Professional red (#dc2626) styling

### ✨ Login Notification Email Includes:
- Login timestamp
- Browser type (Chrome, Firefox, Safari, etc.)
- IP address
- Security warning if suspicious
- Security tips
- Account settings link
- Professional red (#dc2626) styling

### ✨ Password Reset Email Includes:
- Password reset button
- Fallback URL (copy-paste)
- 24-hour expiration warning
- Security tips
- Reassurance section
- Professional red (#dc2626) styling

---

## Testing Checklist

- [ ] Create account and get verification email in console
- [ ] Copy verification URL from console
- [ ] Visit verification URL - see success message
- [ ] Log in with verified account
- [ ] See login notification in console
- [ ] Check that email has all correct details (time, browser, IP)
- [ ] Try password reset
- [ ] See reset email in console
- [ ] Copy reset link and set new password
- [ ] Log in with new password

---

## Common Issues & Fixes

### Issue: Don't see email in console
**Fix**: Make sure `EMAIL_BACKEND = 'console.EmailBackend'` is being used (default for DEBUG=True)

### Issue: Verification URL not working
**Fix**: Copy the full URL including http://localhost:8000

### Issue: Account still marked inactive after verification
**Fix**: Refresh page and try logging in - Django may have cached it

### Issue: See HTML in console instead of formatted email
**Fix**: That's normal! The HTML tags are being printed. It's working correctly.

---

## Email Customization Notes

All email templates have been updated to:
- ✅ Use the red theme (#dc2626) matching your app
- ✅ Use 'Inter' font family matching your app
- ✅ Have professional styling with proper spacing
- ✅ Include security messaging
- ✅ Use emojis for visual appeal
- ✅ Be mobile-responsive
- ✅ Have proper contrast and readability

### Template Locations:
- `tedx_finance/templates/emails/verification_email.html`
- `tedx_finance/templates/emails/login_notification.html`
- `tedx_finance/templates/emails/password_reset.html`

### To Customize Further:
1. Edit any of the HTML files above
2. Changes take effect immediately (no server restart)
3. Test in console backend first
4. No code restart needed!

---

## Next: Production Deployment

Once you've tested locally and are happy with the emails:

1. **Choose Email Provider** (Gmail/SendGrid/AWS)
2. **Get Credentials** (API key or app password)
3. **Set Environment Variables** in your hosting platform
4. **Deploy to Production**
5. **Test with Real Email** - Sign up with real email address
6. **Monitor Email Logs** - Check delivery status

See `EMAIL_SETUP_GUIDE.md` for production setup details.

---

## Dashboard After Login

After successful login, you should be redirected to the dashboard at:
- http://localhost:8000/dashboard

From here you can:
- View your account
- Access settings
- Toggle email notifications
- etc.

---

## Support

If you encounter any issues:
1. Check Django console for error messages
2. Review `EMAIL_SETUP_GUIDE.md` for troubleshooting
3. Check that all environment variables are correct
4. Ensure EMAIL_BACKEND is set for development mode

Enjoy testing! 🚀
