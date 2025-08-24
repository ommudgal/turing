from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from ..database.connection import get_database, get_sync_database


class StudentDatabase:
    """Database operations for students (only verified students)"""

    @staticmethod
    async def create_verified_student(student_data: Dict[str, Any]) -> str:
        """Create a new VERIFIED student in database"""
        try:
            database = await get_database()
            students_collection = database.students

            # Add metadata - only verified students are stored
            student_data["id"] = str(uuid.uuid4())
            student_data["createdAt"] = datetime.utcnow()
            student_data["updatedAt"] = datetime.utcnow()
            student_data["isVerified"] = True
            student_data["verifiedAt"] = datetime.utcnow()

            # Insert verified student
            result = await students_collection.insert_one(student_data)

            if result.inserted_id:
                print(
                    f"✅ Verified student created in database with ID: {student_data['id']}"
                )
                return student_data["id"]
            else:
                raise Exception("Failed to insert verified student")

        except Exception as e:
            print(f"❌ Error creating verified student: {e}")
            raise

    @staticmethod
    async def get_verified_student_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get VERIFIED student by email from database"""
        try:
            database = await get_database()
            students_collection = database.students

            # Only look for verified students
            student = await students_collection.find_one(
                {"studentEmail": email, "isVerified": True}
            )

            if student:
                # Convert ObjectId to string for JSON serialization
                student["_id"] = str(student["_id"])
                print(f"✅ Verified student found: {email}")
                return student
            else:
                print(f"❌ Verified student not found: {email}")
                return None

        except Exception as e:
            print(f"❌ Error getting verified student: {e}")
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
    async def get_all_verified_students() -> list:
        """Get all VERIFIED students from database"""
        try:
            database = await get_database()
            students_collection = database.students

            # Only get verified students
            cursor = students_collection.find({"isVerified": True})
            students = []

            async for student in cursor:
                student["_id"] = str(student["_id"])
                students.append(student)

            print(f"✅ Retrieved {len(students)} verified students from database")
            return students

        except Exception as e:
            print(f"❌ Error getting all verified students: {e}")
            raise
