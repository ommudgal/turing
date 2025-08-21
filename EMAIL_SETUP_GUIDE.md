# 📧 Email Configuration Guide

## Quick Setup for Gmail SMTP

### Step 1: Enable Gmail App Password

1. **Go to Google Account Settings**:
   - Visit: https://myaccount.google.com/
   - Click on "Security" in the left sidebar

2. **Enable 2-Step Verification** (if not already enabled):
   - Under "Signing in to Google", click "2-Step Verification"
   - Follow the setup process

3. **Generate App Password**:
   - In Security settings, click "App passwords"
   - Select "Mail" for the app
   - Select "Other (Custom name)" for device
   - Enter "Trained & Tuned'25" as the name
   - Click "Generate"
   - **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

### Step 2: Configure Backend Environment

Edit the file `backend/.env` and update these values:

```env
# Replace with your actual Gmail details
SMTP_USERNAME=your_actual_email@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
FROM_EMAIL=your_actual_email@gmail.com
ENABLE_EMAIL_SENDING=true
```

### Step 3: Restart the Backend

```bash
# Stop containers
docker-compose down

# Rebuild and start
docker-compose up --build -d
```

## Alternative Email Providers

### Outlook/Hotmail
```env
SMTP_SERVER=smtp.live.com
SMTP_PORT=587
SMTP_USERNAME=your_email@outlook.com
SMTP_PASSWORD=your_password
```

### Yahoo
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your_email@yahoo.com
SMTP_PASSWORD=your_app_password
```

### Custom SMTP Server
```env
SMTP_SERVER=mail.your-domain.com
SMTP_PORT=587
SMTP_USERNAME=noreply@your-domain.com
SMTP_PASSWORD=your_password
```

## Testing Email Configuration

After setup, test with:
```bash
# Check backend logs for email status
docker-compose logs backend --tail 20
```

Look for messages like:
- ✅ `Email sent successfully to email@domain.com with OTP: ABC1`
- ❌ `Failed to send email: [error message]`

## Troubleshooting

### Common Issues:

1. **"Authentication failed"**
   - Double-check Gmail App Password
   - Ensure 2-Step Verification is enabled

2. **"Connection refused"**
   - Check SMTP server and port settings
   - Verify internet connectivity

3. **"Email not received"**
   - Check spam/junk folder
   - Verify recipient email address
   - Check email provider limits

### Fallback Mode

If email fails, the system automatically falls back to console logging:
```
📧 FALLBACK - OTP for user@email.com: ABC1
```

## Security Notes

- ✅ Never commit real passwords to Git
- ✅ Use environment variables for sensitive data
- ✅ App passwords are safer than regular passwords
- ✅ Limit app password scope to email only

## Current Status

- 📧 Email service enhanced with beautiful HTML templates
- 🔒 Secure SMTP authentication
- 🎨 Professional email design with branding
- 🔄 Automatic fallback to console logging
- ⚡ Ready for production use
