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
    store_pending_registration,
    get_pending_registration,
    create_verified_student,
    get_verified_student_by_email,
    get_memory_stats,
)
from ..utils.captcha import verify_recaptcha
from ..database.operations import StudentDatabase

email_service = EmailService()


class StudentController:
    @staticmethod
    async def register_student(student_data: StudentRegistration, request=None):
        """Register a new student (stores in memory until verified)"""
        try:
            print(f"🔍 Registration Debug:")
            print(f"   Received data: {student_data.dict()}")

            # Check for duplicate fields (student number, roll number, email)
            duplicates = await StudentDatabase.check_duplicate_fields(
                student_data.dict()
            )

            duplicate_messages = []
            if duplicates["studentNumber"]:
                duplicate_messages.append("Student number is already registered")
            if duplicates["rollNumber"]:
                duplicate_messages.append(
                    "University roll number is already registered"
                )
            if duplicates["studentEmail"]:
                duplicate_messages.append("College email is already registered")

            if duplicate_messages:
                error_message = (
                    ". ".join(duplicate_messages)
                    + ". Please contact support if you need assistance."
                )
                print(f"❌ Duplicate entries found: {error_message}")
                raise HTTPException(status_code=400, detail=error_message)

            # Check if there's a pending registration
            pending_registration = await get_pending_registration(
                student_data.studentEmail
            )
            if pending_registration:
                print(f"🔄 Resending OTP to pending registration...")
            else:
                print(f"✅ New student registration proceeding...")
                # Store pending registration in memory
                student_dict = student_data.dict()
                await store_pending_registration(
                    student_data.studentEmail, student_dict
                )
                print(f"📝 Pending registration stored in memory")

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

            # Get memory statistics for logging
            stats = await get_memory_stats()
            print(f"📊 Memory stats: {stats}")

            print(f"✅ Registration successful!")
            return {
                "message": "Registration initiated. Please check your email for verification code.",
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
        """Verify OTP and create verified student in database"""
        try:
            # Verify OTP from memory
            is_valid = await verify_otp(verification_data.email, verification_data.otp)

            if not is_valid:
                raise HTTPException(status_code=400, detail="Invalid or expired OTP")

            # Get pending registration data from memory
            pending_data = await get_pending_registration(verification_data.email)
            if not pending_data:
                raise HTTPException(
                    status_code=400,
                    detail="Registration data not found. Please register again.",
                )

            # Create verified student in database
            student_id = await create_verified_student(pending_data)
            print(f"✅ Verified student created in database with ID: {student_id}")

            # Clean up memory storage
            from ..utils.memory_storage import memory_storage

            memory_storage.remove_pending_registration(verification_data.email)

            # Send confirmation email
            await email_service.send_confirmation_email(verification_data.email)

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
            # Check if student is already verified
            verified_student = await get_verified_student_by_email(email)
            if verified_student:
                raise HTTPException(
                    status_code=400,
                    detail="Student is already verified. No need to resend OTP.",
                )

            # Check if there's a pending registration
            pending_data = await get_pending_registration(email)
            if not pending_data:
                raise HTTPException(
                    status_code=404,
                    detail="No pending registration found. Please register first.",
                )

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

    @staticmethod
    async def get_system_stats():
        """Get system statistics for monitoring"""
        try:
            memory_stats = await get_memory_stats()
            return {
                "memory_storage": memory_stats,
                "message": "System statistics retrieved successfully",
                "success": True,
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get system stats: {str(e)}"
            )
