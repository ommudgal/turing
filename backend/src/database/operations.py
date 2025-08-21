from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from ..database.connection import get_database, get_sync_database


class StudentDatabase:
    """Database operations for students"""

    @staticmethod
    async def create_student(student_data: Dict[str, Any]) -> str:
        """Create a new student in database"""
        try:
            database = await get_database()
            students_collection = database.students

            # Add metadata
            student_data["id"] = str(uuid.uuid4())
            student_data["createdAt"] = datetime.utcnow()
            student_data["updatedAt"] = datetime.utcnow()
            student_data["isVerified"] = False

            # Insert student
            result = await students_collection.insert_one(student_data)

            if result.inserted_id:
                print(f"✅ Student created in database with ID: {student_data['id']}")
                return student_data["id"]
            else:
                raise Exception("Failed to insert student")

        except Exception as e:
            print(f"❌ Error creating student: {e}")
            raise

    @staticmethod
    async def get_student_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get student by email from database"""
        try:
            database = await get_database()
            students_collection = database.students

            student = await students_collection.find_one({"studentEmail": email})

            if student:
                # Convert ObjectId to string for JSON serialization
                student["_id"] = str(student["_id"])
                print(f"✅ Student found: {email}")
                return student
            else:
                print(f"❌ Student not found: {email}")
                return None

        except Exception as e:
            print(f"❌ Error getting student: {e}")
            raise

    @staticmethod
    async def update_student_verification(email: str) -> bool:
        """Update student verification status"""
        try:
            database = await get_database()
            students_collection = database.students

            result = await students_collection.update_one(
                {"studentEmail": email},
                {
                    "$set": {
                        "isVerified": True,
                        "verifiedAt": datetime.utcnow(),
                        "updatedAt": datetime.utcnow(),
                    }
                },
            )

            if result.modified_count > 0:
                print(f"✅ Student verification updated: {email}")
                return True
            else:
                print(f"❌ Failed to update verification: {email}")
                return False

        except Exception as e:
            print(f"❌ Error updating verification: {e}")
            raise

    @staticmethod
    async def delete_student_by_email(email: str) -> bool:
        """Delete student by email from database"""
        try:
            database = await get_database()
            students_collection = database.students

            result = await students_collection.delete_one({"studentEmail": email})

            if result.deleted_count > 0:
                print(f"✅ Student deleted: {email}")
                return True
            else:
                print(f"❌ Student not found for deletion: {email}")
                return False

        except Exception as e:
            print(f"❌ Error deleting student: {e}")
            raise

    @staticmethod
    async def get_all_students() -> list:
        """Get all students from database"""
        try:
            database = await get_database()
            students_collection = database.students

            cursor = students_collection.find({})
            students = []

            async for student in cursor:
                student["_id"] = str(student["_id"])
                students.append(student)

            print(f"✅ Retrieved {len(students)} students from database")
            return students

        except Exception as e:
            print(f"❌ Error getting all students: {e}")
            raise


class OTPDatabase:
    """Database operations for OTP storage"""

    @staticmethod
    async def store_otp(email: str, otp: str, expires_in_minutes: int = 10) -> bool:
        """Store OTP in database"""
        try:
            database = await get_database()
            otp_collection = database.otps

            expires_at = datetime.utcnow()
            expires_at = expires_at.replace(
                minute=expires_at.minute + expires_in_minutes
            )

            # Upsert OTP (update if exists, insert if not)
            result = await otp_collection.update_one(
                {"email": email},
                {
                    "$set": {
                        "email": email,
                        "otp": otp,
                        "createdAt": datetime.utcnow(),
                        "expiresAt": expires_at,
                    }
                },
                upsert=True,
            )

            print(f"✅ OTP stored for {email}")
            return True

        except Exception as e:
            print(f"❌ Error storing OTP: {e}")
            return False

    @staticmethod
    async def verify_otp(email: str, otp: str) -> bool:
        """Verify OTP from database"""
        try:
            database = await get_database()
            otp_collection = database.otps

            # Find valid OTP
            stored_otp = await otp_collection.find_one(
                {"email": email, "otp": otp, "expiresAt": {"$gt": datetime.utcnow()}}
            )

            if stored_otp:
                # Delete OTP after verification
                await otp_collection.delete_one({"email": email})
                print(f"✅ OTP verified and deleted for {email}")
                return True
            else:
                print(f"❌ Invalid or expired OTP for {email}")
                return False

        except Exception as e:
            print(f"❌ Error verifying OTP: {e}")
            return False

    @staticmethod
    async def cleanup_expired_otps():
        """Remove expired OTPs from database"""
        try:
            database = await get_database()
            otp_collection = database.otps

            result = await otp_collection.delete_many(
                {"expiresAt": {"$lt": datetime.utcnow()}}
            )

            print(f"✅ Cleaned up {result.deleted_count} expired OTPs")
            return result.deleted_count

        except Exception as e:
            print(f"❌ Error cleaning up OTPs: {e}")
            return 0
