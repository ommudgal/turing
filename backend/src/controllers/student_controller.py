from fastapi import HTTPException
from ..models.student import (
    StudentRegistration,
    StudentResponse,
    OTPVerification,
    OTPResponse,
    CaptchaValidation,
)
from ..utils.email import (
    EmailService,
    generate_otp,
    store_otp,
    verify_otp,
    store_student,
    get_student_by_email,
    update_student_verification,
)
from ..utils.captcha import verify_recaptcha

email_service = EmailService()


class StudentController:
    @staticmethod
    async def register_student(student_data: StudentRegistration):
        """Register a new student"""
        try:
            print(f"🔍 Registration Debug:")
            print(f"   Received data: {student_data.dict()}")

            # Check if student already exists
            existing_student = await get_student_by_email(student_data.studentEmail)
            if existing_student:
                print(f"❌ Student already exists: {student_data.studentEmail}")
                print(f"   Existing student data: {existing_student}")

                # Check if student is already verified
                if existing_student.get("isVerified", False):
                    raise HTTPException(
                        status_code=400,
                        detail="Student is already registered and verified. Please contact support if you need assistance.",
                    )
                else:
                    # Student exists but not verified, resend OTP
                    print(f"🔄 Resending OTP to existing unverified student...")
                    otp = generate_otp()
                    await store_otp(student_data.studentEmail, otp)

                    email_sent = await email_service.send_otp_email(
                        student_data.studentEmail, otp
                    )

                    if email_sent:
                        return {
                            "message": "Student already registered but not verified. New verification code sent to your email.",
                            "student_id": existing_student["id"],
                            "success": True,
                        }
                    else:
                        raise HTTPException(
                            status_code=500, detail="Failed to send verification email"
                        )

            print(f"✅ New student registration proceeding...")

            # Store student data
            student_dict = student_data.dict()
            student_id = await store_student(student_dict)

            print(f"📝 Student stored with ID: {student_id}")

            # Generate and send OTP
            otp = generate_otp()
            await store_otp(student_data.studentEmail, otp)

            print(f"🔑 OTP generated: {otp}")

            # Send OTP email
            email_sent = await email_service.send_otp_email(
                student_data.studentEmail, otp
            )

            if not email_sent:
                print(f"❌ Failed to send email")
                raise HTTPException(
                    status_code=500, detail="Failed to send verification email"
                )

            print(f"✅ Registration successful!")
            return {
                "message": "Student registered successfully. Please check your email for verification code.",
                "student_id": student_id,
                "success": True,
            }

        except HTTPException as e:
            print(f"❌ HTTP Exception: {e.detail}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Registration failed: {str(e)}"
            )

    @staticmethod
    async def verify_otp(verification_data: OTPVerification):
        """Verify OTP for student"""
        try:
            # Verify OTP
            is_valid = await verify_otp(verification_data.email, verification_data.otp)

            if not is_valid:
                raise HTTPException(status_code=400, detail="Invalid or expired OTP")

            # Update student verification status
            await update_student_verification(verification_data.email)

            return OTPResponse(
                message="Email verified successfully! Registration completed.",
                success=True,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Verification failed: {str(e)}"
            )

    @staticmethod
    async def resend_otp(email: str):
        """Resend OTP to student"""
        try:
            # Check if student exists
            student = await get_student_by_email(email)
            if not student:
                raise HTTPException(status_code=404, detail="Student not found")

            # Generate new OTP
            otp = generate_otp()
            await store_otp(email, otp)

            # Send OTP email
            email_sent = await email_service.send_otp_email(email, otp)

            if not email_sent:
                raise HTTPException(
                    status_code=500, detail="Failed to send verification email"
                )

            return {"message": "Verification code sent successfully", "success": True}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to resend OTP: {str(e)}"
            )

    @staticmethod
    async def validate_captcha(captcha_data: CaptchaValidation):
        """Validate reCAPTCHA"""
        try:
            is_valid = await verify_recaptcha(captcha_data.recaptchaValue)

            if not is_valid:
                raise HTTPException(status_code=400, detail="Invalid reCAPTCHA")

            return {"message": "reCAPTCHA validated successfully", "success": True}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"reCAPTCHA validation failed: {str(e)}"
            )
