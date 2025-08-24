import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import asyncio
from dotenv import load_dotenv

load_dotenv()


class Database:
    client: AsyncIOMotorClient = None
    sync_client: MongoClient = None


# MongoDB connection
db = Database()


async def get_database():
    """Get async database connection"""
    if db.client is None:
        await connect_to_mongo()
    return db.client.trained_tuned_2025


def get_sync_database():
    """Get sync database connection"""
    if db.sync_client is None:
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            raise Exception("MONGODB_URI not found in environment variables")
        db.sync_client = MongoClient(mongodb_uri)
    return db.sync_client.trained_tuned_2025


async def connect_to_mongo():
    """Create database connection"""
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        raise Exception("MONGODB_URI not found in environment variables")

    print("🔗 Connecting to MongoDB...")

    # Async client for FastAPI
    db.client = AsyncIOMotorClient(mongodb_uri)

    # Sync client for non-async operations
    db.sync_client = MongoClient(mongodb_uri)

    # Test connection
    try:
        await db.client.admin.command("ping")
        print("✅ MongoDB connection successful!")

        # Create indexes
        database = db.client.trained_tuned_2025
        students_collection = database.students

        # Create unique indexes on critical fields
        await students_collection.create_index("studentEmail", unique=True)
        await students_collection.create_index("studentNumber", unique=True)
        await students_collection.create_index("rollNumber", unique=True)
        print("✅ Database indexes created successfully!")

        # Create compound index for efficient duplicate checking
        await students_collection.create_index(
            [
                ("studentEmail", 1),
                ("studentNumber", 1),
                ("rollNumber", 1),
                ("isVerified", 1),
            ]
        )
        print("✅ Compound index for duplicate checking created!")

    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise


async def close_mongo_connection():
    """Close database connection"""
    print("🔌 Closing MongoDB connection...")
    if db.client:
        db.client.close()
    if db.sync_client:
        db.sync_client.close()
