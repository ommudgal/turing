"""
In-memory storage for pending registrations and OTPs
This prevents database flooding with unverified entries
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import threading


class MemoryStorage:
    """Thread-safe in-memory storage for pending registrations and OTPs"""

    def __init__(self):
        self._pending_registrations: Dict[str, Dict[str, Any]] = {}
        self._otps: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

        # Start cleanup task
        self._start_cleanup_task()

    def store_pending_registration(
        self, email: str, student_data: Dict[str, Any]
    ) -> None:
        """Store pending registration data in memory"""
        with self._lock:
            self._pending_registrations[email] = {
                "data": student_data,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow()
                + timedelta(minutes=30),  # 30 min expiry
            }
        print(f"📝 Pending registration stored in memory for: {email}")

    def get_pending_registration(self, email: str) -> Optional[Dict[str, Any]]:
        """Get pending registration data from memory"""
        with self._lock:
            if email in self._pending_registrations:
                entry = self._pending_registrations[email]
                if datetime.utcnow() <= entry["expires_at"]:
                    return entry["data"]
                else:
                    # Remove expired entry
                    del self._pending_registrations[email]
            return None

    def remove_pending_registration(self, email: str) -> None:
        """Remove pending registration from memory"""
        with self._lock:
            if email in self._pending_registrations:
                del self._pending_registrations[email]
                print(f"🗑️ Pending registration removed from memory: {email}")

    def store_otp(self, email: str, otp: str, expires_in_minutes: int = 2) -> None:
        """Store OTP in memory"""
        with self._lock:
            self._otps[email] = {
                "otp": otp,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(minutes=expires_in_minutes),
            }
        print(
            f"🔑 OTP stored in memory for: {email} (expires in {expires_in_minutes} min)"
        )

    def verify_otp(self, email: str, otp: str) -> bool:
        """Verify OTP from memory"""
        with self._lock:
            if email in self._otps:
                entry = self._otps[email]
                if datetime.utcnow() <= entry["expires_at"] and entry["otp"] == otp:
                    # Remove OTP after successful verification
                    del self._otps[email]
                    print(f"✅ OTP verified and removed from memory: {email}")
                    return True
                elif datetime.utcnow() > entry["expires_at"]:
                    # Remove expired OTP
                    del self._otps[email]
                    print(f"⏰ OTP expired and removed from memory: {email}")

        print(f"❌ Invalid or expired OTP for: {email}")
        return False

    def cleanup_expired_entries(self) -> None:
        """Remove expired entries from memory"""
        current_time = datetime.utcnow()

        with self._lock:
            # Cleanup expired pending registrations
            expired_registrations = [
                email
                for email, entry in self._pending_registrations.items()
                if current_time > entry["expires_at"]
            ]
            for email in expired_registrations:
                del self._pending_registrations[email]

            # Cleanup expired OTPs
            expired_otps = [
                email
                for email, entry in self._otps.items()
                if current_time > entry["expires_at"]
            ]
            for email in expired_otps:
                del self._otps[email]

            if expired_registrations or expired_otps:
                print(
                    f"🧹 Cleaned up {len(expired_registrations)} expired registrations "
                    f"and {len(expired_otps)} expired OTPs from memory"
                )

    def get_stats(self) -> Dict[str, int]:
        """Get current memory storage statistics"""
        with self._lock:
            return {
                "pending_registrations": len(self._pending_registrations),
                "active_otps": len(self._otps),
            }

    def _start_cleanup_task(self) -> None:
        """Start background cleanup task"""

        def cleanup_loop():
            while True:
                try:
                    self.cleanup_expired_entries()
                    # Run cleanup every 5 minutes
                    threading.Event().wait(300)
                except Exception as e:
                    print(f"❌ Error in memory cleanup: {e}")
                    threading.Event().wait(60)  # Wait 1 minute on error

        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
        print("🧹 Memory cleanup task started")


# Global instance
memory_storage = MemoryStorage()
