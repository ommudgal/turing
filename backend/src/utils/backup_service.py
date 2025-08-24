"""
Automated CSV backup service for database
Exports verified students to CSV files with automatic scheduling
"""

import csv
import os
import asyncio
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any
from ..database.operations import StudentDatabase


class BackupService:
    """Service for automated database backups to CSV"""

    def __init__(self, backup_dir: str = "/app/backups"):
        self.backup_dir = backup_dir
        self.backup_filename = "students_backup.csv"
        self.backup_interval_hours = 2  # Backup every 2 hours
        self._scheduler_started = False
        self._ensure_backup_directory()

    def start_scheduler(self):
        """Start the backup scheduler (call this after app startup)"""
        if not self._scheduler_started:
            self._start_backup_scheduler()
            self._scheduler_started = True

    def _ensure_backup_directory(self):
        """Create backup directory if it doesn't exist"""
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            print(f"📁 Backup directory ensured: {self.backup_dir}")
        except Exception as e:
            print(f"❌ Error creating backup directory: {e}")
            # Fallback to current directory
            self.backup_dir = "/app"
            print(f"📁 Using fallback directory: {self.backup_dir}")

    async def create_csv_backup(self) -> bool:
        """Create CSV backup of all verified students"""
        return await self._sync_backup()

    def _backup_loop(self):
        """Background loop for scheduled backups"""
        while True:
            try:
                print(f"💾 Starting database backup...")

                # Use threading event to control timing
                event = threading.Event()
                success = False

                # Create a simple sync wrapper for the async backup
                def run_backup():
                    nonlocal success
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        success = loop.run_until_complete(self._sync_backup())
                        loop.close()
                    except Exception as e:
                        print(f"❌ Backup error: {e}")
                        success = False

                # Run backup in a separate thread to avoid loop conflicts
                backup_thread = threading.Thread(target=run_backup)
                backup_thread.start()
                backup_thread.join(timeout=60)  # 60 second timeout

                if success:
                    print(
                        f"🔄 Next backup scheduled in {self.backup_interval_hours} hours"
                    )
                    wait_seconds = self.backup_interval_hours * 3600
                else:
                    print(f"⚠️ Backup failed, retrying in 30 minutes")
                    wait_seconds = 1800  # 30 minutes

                # Wait for next backup
                event.wait(wait_seconds)

            except Exception as e:
                print(f"❌ Error in backup scheduler: {e}")
                # Wait 5 minutes on error
                threading.Event().wait(300)

    async def _sync_backup(self) -> bool:
        """Sync version of backup to avoid loop conflicts"""
        try:
            # Get all verified students
            students = await StudentDatabase.get_all_verified_students()

            if not students:
                print("ℹ️ No verified students to backup")
                return True

            # Define CSV headers - updated for current schema
            headers = [
                "id",
                "fullName",
                "studentEmail",
                "studentNumber",
                "rollNumber",
                "branch",
                "gender",
                "scholar",
                "mobileNumber",
                "domain",
                "isVerified",
                "createdAt",
                "updatedAt",
                "verifiedAt",
            ]

            # Create backup file path
            backup_path = os.path.join(self.backup_dir, self.backup_filename)

            # Write CSV file (overwrite existing)
            with open(backup_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()

                for student in students:
                    # Format datetime fields for CSV
                    formatted_student = {}
                    for key in headers:
                        value = student.get(key, "")
                        if isinstance(value, datetime):
                            formatted_student[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            formatted_student[key] = value

                    writer.writerow(formatted_student)

            # Get file size for logging
            file_size = os.path.getsize(backup_path)
            size_kb = file_size / 1024

            print(f"✅ Backup completed successfully!")
            print(f"   📊 Students backed up: {len(students)}")
            print(f"   📁 File: {backup_path}")
            print(f"   💾 Size: {size_kb:.2f} KB")
            print(
                f"   🕒 Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
            )

            return True

        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False

    def _start_backup_scheduler(self):
        """Start the background backup scheduler"""
        backup_thread = threading.Thread(target=self._backup_loop, daemon=True)
        backup_thread.start()
        print(f"⏰ Backup scheduler started (every {self.backup_interval_hours} hours)")

        # Run initial backup after 5 minutes - simplified to avoid loop conflicts
        def initial_backup():
            threading.Event().wait(300)  # Wait 5 minutes
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._sync_backup())
                loop.close()
            except Exception as e:
                print(f"❌ Initial backup failed: {e}")

        initial_thread = threading.Thread(target=initial_backup, daemon=True)
        initial_thread.start()
        print("🚀 Initial backup scheduled in 5 minutes")

    async def get_backup_info(self) -> Dict[str, Any]:
        """Get backup file information"""
        try:
            backup_path = os.path.join(self.backup_dir, self.backup_filename)

            if not os.path.exists(backup_path):
                return {"exists": False, "message": "No backup file found"}

            # Get file stats
            stat = os.stat(backup_path)
            file_size = stat.st_size
            modified_time = datetime.fromtimestamp(stat.st_mtime)

            # Count lines in CSV (excluding header)
            with open(backup_path, "r", encoding="utf-8") as f:
                line_count = sum(1 for line in f) - 1  # Subtract header

            return {
                "exists": True,
                "path": backup_path,
                "size_bytes": file_size,
                "size_kb": file_size / 1024,
                "last_modified": modified_time.strftime("%Y-%m-%d %H:%M:%S"),
                "student_count": line_count,
                "next_backup_in_hours": self.backup_interval_hours,
            }

        except Exception as e:
            return {"exists": False, "error": str(e)}

    async def force_backup(self) -> bool:
        """Force an immediate backup"""
        print("🔧 Manual backup initiated...")
        return await self._sync_backup()


# Global backup service instance
backup_service = BackupService()
