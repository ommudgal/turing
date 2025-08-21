#!/usr/bin/env python3
"""
MongoDB Status Check Script
"""
import pymongo
import os
from datetime import datetime


def check_mongodb_status():
    """Check MongoDB integration status"""
    try:
        print("🔍 MongoDB Integration Status Check")
        print("=" * 50)

        # Connect to MongoDB
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            print("❌ MONGODB_URI not found!")
            return

        print(f"🔗 Connecting to: {mongodb_uri[:50]}...")
        client = pymongo.MongoClient(mongodb_uri)

        # Test connection
        client.admin.command("ping")
        print("✅ MongoDB connection successful!")

        # Access database
        db = client.trained_tuned_2025

        # Check students collection
        students_collection = db.students
        student_count = students_collection.count_documents({})
        print(f"👥 Students in database: {student_count}")

        if student_count > 0:
            print("\n📋 Student List:")
            for i, student in enumerate(students_collection.find({}), 1):
                print(
                    f"   {i}. {student.get('fullName', 'N/A')} ({student.get('studentEmail', 'N/A')})"
                )
                print(f"      Verified: {student.get('isVerified', False)}")
                print(f"      Created: {student.get('createdAt', 'N/A')}")

        # Check OTPs collection
        otps_collection = db.otps
        otp_count = otps_collection.count_documents({})
        print(f"\n🔑 Active OTPs: {otp_count}")

        if otp_count > 0:
            print("\n📋 OTP List:")
            for i, otp in enumerate(otps_collection.find({}), 1):
                expires_at = otp.get("expiresAt", "N/A")
                status = (
                    "Expired"
                    if expires_at != "N/A" and expires_at < datetime.utcnow()
                    else "Active"
                )
                print(
                    f"   {i}. {otp.get('email', 'N/A')} - OTP: {otp.get('otp', 'N/A')} ({status})"
                )

        # List all collections
        collections = db.list_collection_names()
        print(f"\n📊 Database collections: {collections}")

        client.close()
        print("\n" + "=" * 50)
        print("✅ MongoDB status check completed!")

    except Exception as e:
        print(f"❌ Error checking MongoDB: {e}")


if __name__ == "__main__":
    check_mongodb_status()
