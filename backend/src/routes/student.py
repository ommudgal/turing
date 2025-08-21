from fastapi import APIRouter, HTTPException, Request
from ..controllers.student_controller import StudentController
from ..models.student import StudentRegistration, OTPVerification, CaptchaValidation

router = APIRouter()

# Simple in-memory session storage for demo (use Redis or database in production)
session_storage = {}


@router.post("/register")
async def register_student(student_data: StudentRegistration, request: Request):
    """Register a new student"""
    result = await StudentController.register_student(student_data)
    # Store email in session for OTP resend functionality
    client_ip = request.client.host
    session_storage[client_ip] = student_data.studentEmail
    return result


@router.post("/verify")
async def verify_student(verification_data: OTPVerification):
    """Verify student OTP"""
    return await StudentController.verify_otp(verification_data)


@router.get("/resend-otp")
async def resend_otp(request: Request):
    """Resend OTP to student"""
    # Get email from session storage based on client IP
    client_ip = request.client.host
    email = session_storage.get(client_ip)

    if not email:
        # Fallback: check query parameter
        email = request.query_params.get("email")
        if not email:
            raise HTTPException(
                status_code=400,
                detail="No active session found. Please register again.",
            )

    return await StudentController.resend_otp(email)


@router.post("/validate")
async def validate_captcha(captcha_data: CaptchaValidation):
    """Validate reCAPTCHA"""
    return await StudentController.validate_captcha(captcha_data)
