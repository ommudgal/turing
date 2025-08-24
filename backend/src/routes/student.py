from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..controllers.student_controller import StudentController
from ..models.student import StudentRegistration, OTPVerification, CaptchaValidation

router = APIRouter()

# Initialize rate limiter for this router
limiter = Limiter(key_func=get_remote_address)

# Simple in-memory session storage for demo (use Redis or database in production)
session_storage = {}


@router.post("/register")
@limiter.limit("3/minute")  # Maximum 3 registrations per minute per IP
async def register_student(request: Request, student_data: StudentRegistration):
    """Register a new student"""
    result = await StudentController.register_student(student_data, request)
    # Store email in session for OTP resend functionality
    client_ip = request.client.host if request.client else "unknown"
    session_storage[client_ip] = student_data.studentEmail
    return result


@router.post("/verify")
@limiter.limit("10/minute")  # Maximum 10 OTP verification attempts per minute per IP
async def verify_student(request: Request, verification_data: OTPVerification):
    """Verify student OTP"""
    return await StudentController.verify_otp(verification_data)


@router.get("/resend-otp")
@limiter.limit("1/2minutes")  # Maximum 1 OTP resend every 2 minutes per IP
async def resend_otp(request: Request):
    """Resend OTP to student"""
    # Get email from session storage based on client IP
    client_ip = request.client.host if request.client else "unknown"
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
@limiter.limit("5/minute")  # Maximum 5 captcha validations per minute per IP
async def validate_captcha(request: Request, captcha_data: CaptchaValidation):
    """Validate reCAPTCHA"""
    return await StudentController.validate_captcha(captcha_data)


@router.get("/stats")
@limiter.limit("10/minute")  # Maximum 10 stats requests per minute per IP
async def get_system_stats(request: Request):
    """Get system statistics (for monitoring)"""
    return await StudentController.get_system_stats()


@router.get("/backup/info")
@limiter.limit("20/minute")  # Maximum 20 backup info requests per minute per IP
async def get_backup_info(request: Request):
    """Get backup file information"""
    return await StudentController.get_backup_info()


@router.post("/backup/force")
@limiter.limit("2/hour")  # Maximum 2 manual backups per hour per IP
async def force_backup(request: Request):
    """Force an immediate backup"""
    return await StudentController.force_backup()
