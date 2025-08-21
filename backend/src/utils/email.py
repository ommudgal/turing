import aiosmtplib
import asyncio
import random
import string
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from typing import Dict, Optional
from ..database.operations import StudentDatabase, OTPDatabase

load_dotenv()

# In-memory storage for demo purposes (replace with database in production)
students_db = {}
otp_storage = {}


class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)

    async def send_otp_email(self, to_email: str, otp: str):
        """Send OTP via email"""
        try:
            # Check if email sending is enabled
            enable_email = os.getenv("ENABLE_EMAIL_SENDING", "false").lower() == "true"

            print(f"🔧 Email Settings Debug:")
            print(f"   SMTP Server: {self.smtp_server}")
            print(f"   SMTP Port: {self.smtp_port}")
            print(f"   Username: {self.smtp_username}")
            print(f"   From Email: {self.from_email}")
            print(f"   Password Set: {'Yes' if self.smtp_password else 'No'}")
            print(f"   Email Enabled: {enable_email}")

            if not enable_email or not self.smtp_username or not self.smtp_password:
                # Fallback to console logging for demo/development
                print(f"📧 EMAIL DEMO MODE - OTP for {to_email}: {otp}")
                print("💡 To enable real emails, configure SMTP settings in .env file")
                return True

            message = MIMEMultipart()
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = "🔐 Verification Code - Trained & Tuned'25"

            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; color: white;">
                    <h1 style="margin: 0; font-size: 28px;">🎓 Trained & Tuned'25</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Student Registration Portal</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; margin: 20px 0;">
                    <h2 style="color: #333; margin-top: 0;">Welcome! Almost there...</h2>
                    <p style="color: #555; font-size: 16px; line-height: 1.6;">
                        Thank you for registering for Trained & Tuned'25! To complete your registration, 
                        please verify your email address using the code below:
                    </p>
                    
                    <div style="background: white; border: 2px dashed #667eea; border-radius: 8px; padding: 20px; text-align: center; margin: 25px 0;">
                        <p style="color: #667eea; font-size: 14px; margin: 0 0 10px 0; font-weight: bold;">VERIFICATION CODE</p>
                        <div style="font-size: 32px; font-weight: bold; color: #333; letter-spacing: 8px; font-family: monospace;">
                            {otp}
                        </div>
                    </div>
                    
                    <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 6px; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0; color: #856404; font-size: 14px;">
                            ⏰ <strong>Important:</strong> This code will expire in 10 minutes for security reasons.
                        </p>
                    </div>
                    
                    <p style="color: #555; font-size: 14px; line-height: 1.6;">
                        Enter this code in the verification screen to complete your registration. 
                        If you didn't request this code, please ignore this email.
                    </p>
                </div>
                
                <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
                    <p style="margin: 0;">© 2025 Trained & Tuned'25 Event | Student Registration System</p>
                    <p style="margin: 5px 0 0 0;">This is an automated message, please do not reply.</p>
                </div>
            </body>
            </html>
            """

            message.attach(MIMEText(body, "html"))

            print(f"📤 Attempting to send email to {to_email}...")

            # Send the actual email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_username,
                password=self.smtp_password,
            )

            print(f"✅ Email sent successfully to {to_email} with OTP: {otp}")
            return True

        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
            # Fallback to console logging if email fails
            print(f"📧 FALLBACK - OTP for {to_email}: {otp}")
            return True  # Return True so registration doesn't fail


def generate_otp() -> str:
    """Generate a 5-character OTP with 2 letters and 3 numbers"""
    # Generate 2 random uppercase letters
    letters = random.choices(string.ascii_uppercase, k=2)
    # Generate 3 random digits
    numbers = random.choices(string.digits, k=3)

    # Combine and shuffle to randomize positions
    otp_chars = letters + numbers
    random.shuffle(otp_chars)

    return "".join(otp_chars)


async def store_otp(email: str, otp: str):
    """Store OTP for verification (MongoDB)"""
    return await OTPDatabase.store_otp(email, otp)


async def verify_otp(email: str, otp: str) -> bool:
    """Verify OTP (MongoDB)"""
    return await OTPDatabase.verify_otp(email, otp)


async def store_student(student_data: dict) -> str:
    """Store student data (MongoDB)"""
    return await StudentDatabase.create_student(student_data)


async def get_student_by_email(email: str) -> Optional[Dict]:
    """Get student by email (MongoDB)"""
    return await StudentDatabase.get_student_by_email(email)


async def update_student_verification(email: str):
    """Mark student as verified (MongoDB)"""
    return await StudentDatabase.update_student_verification(email)


async def delete_student_by_email(email: str) -> bool:
    """Delete student by email (MongoDB)"""
    return await StudentDatabase.delete_student_by_email(email)
