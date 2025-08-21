from pydantic import BaseModel, EmailStr
from typing import Optional


class StudentRegistration(BaseModel):
    fullName: str
    branch: str
    rollNumber: str
    gender: str
    scholar: str
    studentNumber: str
    studentEmail: EmailStr
    mobileNumber: str
    domain: str


class StudentResponse(BaseModel):
    id: int
    fullName: str
    branch: str
    rollNumber: str
    gender: str
    scholar: str
    studentNumber: str
    studentEmail: str
    mobileNumber: str
    domain: str
    isVerified: bool


class OTPVerification(BaseModel):
    otp: str
    email: EmailStr


class CaptchaValidation(BaseModel):
    recaptchaValue: str


class OTPResponse(BaseModel):
    message: str
    success: bool
