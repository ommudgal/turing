#!/usr/bin/env python3
"""
Email Configuration Test Script
Run this to test your SMTP settings before deploying
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.email import EmailService


async def test_email_config():
    """Test email configuration"""
    print("🧪 Testing Email Configuration...")
    print("-" * 50)

    # Initialize email service
    email_service = EmailService()

    # Check configuration
    print(f"📧 SMTP Server: {email_service.smtp_server}")
    print(f"🔌 SMTP Port: {email_service.smtp_port}")
    print(f"👤 Username: {email_service.smtp_username}")
    print(f"📨 From Email: {email_service.from_email}")
    print(f"🔑 Password Set: {'Yes' if email_service.smtp_password else 'No'}")
    print()

    # Get test email
    test_email = input("Enter your email address to test: ").strip()
    if not test_email:
        print("❌ No email provided. Exiting...")
        return

    print(f"\n📤 Sending test OTP to: {test_email}")

    # Send test email
    try:
        success = await email_service.send_otp_email(test_email, "TEST")
        if success:
            print("✅ Test email sent successfully!")
            print("📬 Check your email inbox (and spam folder)")
        else:
            print("❌ Failed to send test email")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_email_config())
