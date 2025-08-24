import requests
import os
from dotenv import load_dotenv

load_dotenv()

RECAPTCHA_SECRET_KEY = os.getenv(
    "RECAPTCHA_SECRET_KEY", "6LfGaa8rAAAAADTNAJk9l5AfHf4gg0FXEJZ_b31k"
)


async def verify_recaptcha(recaptcha_response: str) -> bool:
    """Verify reCAPTCHA response"""
    try:
        print(f"🤖 reCAPTCHA token received: {recaptcha_response}")

        # reCAPTCHA verification (works with both standard and Enterprise)
        url = "https://www.google.com/recaptcha/api/siteverify"
        data = {"secret": RECAPTCHA_SECRET_KEY, "response": recaptcha_response}

        response = requests.post(url, data=data, timeout=10)
        result = response.json()

        success = result.get("success", False)
        score = result.get("score", 0)  # For v3

        print(f"🔍 reCAPTCHA verification result:")
        print(f"   Success: {success}")
        print(f"   Score: {score}")
        print(f"   Full response: {result}")

        # For v2 invisible, just check success
        # For v3, you might want to check score > 0.5
        return success

    except Exception as e:
        print(f"❌ reCAPTCHA verification error: {str(e)}")
        return False
