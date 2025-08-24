from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional
import re


class StudentRegistration(BaseModel):
    fullName: str
    branch: str
    rollNumber: str
    gender: str
    scholar: str
    studentNumber: str = Field(..., min_length=7, max_length=20)
    studentEmail: EmailStr
    mobileNumber: str = Field(..., min_length=10, max_length=10)
    domain: str

    @validator("studentNumber")
    def validate_student_number(cls, v):
        if not v.startswith("24"):
            raise ValueError("Student number must start with 24")
        if not re.match(r"^24[0-9]{5,18}$", v):
            raise ValueError(
                "Student number must start with 24 and be 7-20 characters long"
            )
        return v

    @validator("studentEmail")
    def validate_student_email(cls, v):
        if not str(v).endswith("@akgec.ac.in"):
            raise ValueError("College email must belong to akgec.ac.in domain")
        return v

    @validator("studentEmail")
    def validate_email_student_number_match(cls, v, values):
        if "studentNumber" in values:
            student_number = values["studentNumber"]
            if student_number not in str(v):
                raise ValueError(f"Email must contain student number {student_number}")
        return v

    @validator("mobileNumber")
    def validate_mobile_number(cls, v):
        if not re.match(r"^[0-9]{10}$", v):
            raise ValueError("Mobile number must be exactly 10 digits")
        return v


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
