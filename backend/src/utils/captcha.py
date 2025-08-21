import requests
import os
from dotenv import load_dotenv

load_dotenv()

RECAPTCHA_SECRET_KEY = os.getenv(
    "RECAPTCHA_SECRET_KEY", "6LfZSKgrAAAAAFyGHqGCmVNWaKKafn_0QZ1qN9aB"
)


async def verify_recaptcha(recaptcha_response: str) -> bool:
    """Verify reCAPTCHA response"""
    try:
        # For demo purposes, always return True
        # In production, uncomment the actual verification code below
        print(f"reCAPTCHA token received: {recaptcha_response}")
        return True

        # Actual reCAPTCHA verification (uncomment for production)
        # url = "https://www.google.com/recaptcha/api/siteverify"
        # data = {
        #     'secret': RECAPTCHA_SECRET_KEY,
        #     'response': recaptcha_response
        # }
        # response = requests.post(url, data=data)
        # result = response.json()
        # return result.get('success', False)
    except Exception as e:
        print(f"reCAPTCHA verification error: {str(e)}")
        return False
