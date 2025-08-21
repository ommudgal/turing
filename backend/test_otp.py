#!/usr/bin/env python3
"""
OTP Generation Test Script
Test the new 5-character OTP format (2 letters + 3 numbers)
"""

import sys
import re
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.email import generate_otp


def test_otp_format():
    """Test that OTP has correct format: 2 letters + 3 numbers"""
    print("🧪 Testing New OTP Format (2 letters + 3 numbers)...")
    print("-" * 50)

    # Generate multiple OTPs to test consistency
    for i in range(10):
        otp = generate_otp()

        # Count letters and numbers
        letters = len(re.findall(r"[A-Z]", otp))
        numbers = len(re.findall(r"[0-9]", otp))

        # Check format
        is_valid = len(otp) == 5 and letters == 2 and numbers == 3

        status = "✅" if is_valid else "❌"
        print(f"{status} OTP #{i+1:2d}: {otp} (Letters: {letters}, Numbers: {numbers})")

        if not is_valid:
            print(f"    ❌ FAILED: Expected 5 chars (2 letters + 3 numbers)")
            return False

    print("\n🎉 All OTPs passed the format test!")
    print("✅ Format: 5 characters with exactly 2 letters and 3 numbers")
    return True


if __name__ == "__main__":
    test_otp_format()
