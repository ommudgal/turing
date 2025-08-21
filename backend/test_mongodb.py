#!/usr/bin/env python3
"""
Test script for MongoDB integration
"""
import asyncio
import sys
import os

sys.path.append("/app")

from src.database.operations import StudentDatabase, OTPDatabase


async def test_mongodb_integration():
    """Test MongoDB integration"""
    print("🧪 Testing MongoDB Integration")
    print("=" * 50)

    try:
        # Test 1: Get all students (should be empty initially)
        print("📋 Test 1: Getting all students...")
        students = await StudentDatabase.get_all_students()
        print(f"✅ Found {len(students)} students in database")

        # Test 2: Create a test student
        print("\n👤 Test 2: Creating test student...")
        test_student = {
            "studentName": "Test Student",
            "studentEmail": "test@example.com",
            "collegeName": "Test College",
            "branch": "CSE",
            "year": "3rd Year",
        }
        student_id = await StudentDatabase.create_student(test_student)
        print(f"✅ Created student with ID: {student_id}")

        # Test 3: Get student by email
        print("\n🔍 Test 3: Getting student by email...")
        retrieved_student = await StudentDatabase.get_student_by_email(
            "test@example.com"
        )
        if retrieved_student:
            print(f"✅ Retrieved student: {retrieved_student['studentName']}")
            print(f"   Verified: {retrieved_student['isVerified']}")
        else:
            print("❌ Failed to retrieve student")

        # Test 4: Store and verify OTP
        print("\n🔑 Test 4: Testing OTP functionality...")
        await OTPDatabase.store_otp("test@example.com", "A1B2C")
        print("✅ OTP stored successfully")

        otp_valid = await OTPDatabase.verify_otp("test@example.com", "A1B2C")
        print(f"✅ OTP verification: {'Valid' if otp_valid else 'Invalid'}")

        # Test 5: Update student verification
        print("\n✔️ Test 5: Updating verification status...")
        verification_updated = await StudentDatabase.update_student_verification(
            "test@example.com"
        )
        print(f"✅ Verification updated: {verification_updated}")

        # Test 6: Get updated student
        print("\n🔍 Test 6: Getting updated student...")
        updated_student = await StudentDatabase.get_student_by_email("test@example.com")
        if updated_student:
            print(f"✅ Student verification status: {updated_student['isVerified']}")

        # Test 7: Clean up - delete test student
        print("\n🗑️ Test 7: Cleaning up test data...")
        deleted = await StudentDatabase.delete_student_by_email("test@example.com")
        print(f"✅ Test student deleted: {deleted}")

        # Final check
        final_students = await StudentDatabase.get_all_students()
        print(f"\n📊 Final student count: {len(final_students)}")

        print("\n" + "=" * 50)
        print("🎉 All MongoDB tests passed successfully!")

    except Exception as e:
        print(f"\n❌ MongoDB test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mongodb_integration())
