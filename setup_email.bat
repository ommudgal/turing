@echo off
echo.
echo ================================================================
echo            📧 Email Configuration Setup for 
echo                    Trained & Tuned'25
echo ================================================================
echo.
echo This script will help you configure Gmail SMTP for sending OTPs.
echo.

set /p gmail_email="Enter your Gmail address: "
set /p gmail_password="Enter your Gmail App Password (16 characters): "

echo.
echo Updating .env file...

(
echo # Email Configuration ^(Gmail SMTP^)
echo SMTP_SERVER=smtp.gmail.com
echo SMTP_PORT=587
echo SMTP_USERNAME=%gmail_email%
echo SMTP_PASSWORD=%gmail_password%
echo FROM_EMAIL=%gmail_email%
echo.
echo # Application Settings
echo APP_NAME=Trained ^& Tuned'25
echo ENABLE_EMAIL_SENDING=true
echo.
echo # reCAPTCHA ^(optional^)
echo RECAPTCHA_SECRET_KEY=6LfZSKgrAAAAAFyGHqGCmVNWaKKafn_0QZ1qN9aB
) > backend\.env

echo.
echo ✅ Configuration saved to backend\.env
echo.
echo Next steps:
echo 1. Run: docker-compose down
echo 2. Run: docker-compose up --build -d
echo 3. Test the registration form
echo.
echo 📋 Need help getting Gmail App Password?
echo    Visit: https://myaccount.google.com/apppasswords
echo.
pause
