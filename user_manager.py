import hashlib
import secrets
import sqlite3
from typing import Optional, Dict, List

# ============================================================================
# DEFAULT ADMIN CREDENTIALS - USED ONLY ON FIRST RUN TO SEED USER TABLE
# CHANGE THESE BEFORE FIRST RUN TO SET YOUR OWN DEFAULT ADMIN ACCOUNT.
# ============================================================================
DEFAULT_ADMIN_USERNAME = "admin"
# NOTE: this defaults to 'admin' to match the README and UI hint. Change
# before first run to a secure password for production.
DEFAULT_ADMIN_PASSWORD = "admin"
# ============================================================================


def hash_password(password: str) -> str:
    """Create a salted password hash using SHA-256."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()
    return f"{salt}${hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against the stored salted hash."""
    if not stored_hash or "$" not in stored_hash:
        return False
    salt, hashed = stored_hash.split("$", 1)
    candidate = hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()
    return secrets.compare_digest(candidate, hashed)


class UserManager:
    """Simple user manager that stores accounts inside the same SQLite DB."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_user_table()
        self._ensure_default_admin()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_user_table(self):
        conn = self._connect()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def _ensure_default_admin(self):
        if not self.get_user(DEFAULT_ADMIN_USERNAME):
            self.create_user(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD, role="admin")

    def get_user(self, username: str) -> Optional[Dict[str, str]]:
        conn = self._connect()
        try:
            cur = conn.execute(
                "SELECT username, password_hash, role FROM users WHERE username = ?",
                (username,),
            )
            row = cur.fetchone()
            if row:
                return {"username": row[0], "password_hash": row[1], "role": row[2]}
            return None
        finally:
            conn.close()

    def list_users(self) -> List[Dict[str, str]]:
        conn = self._connect()
        try:
            cur = conn.execute(
                "SELECT username, role, created_at FROM users ORDER BY created_at ASC"
            )
            return [
                {"username": row[0], "role": row[1], "created_at": row[2]}
                for row in cur.fetchall()
            ]
        finally:
            conn.close()

    def create_user(self, username: str, password: str, role: str = "user"):
        username = (username or "").strip()
        if not username:
            raise ValueError("Username cannot be empty.")
        if not password:
            raise ValueError("Password cannot be empty.")
        role = (role or "user").lower()
        if role not in ("user", "admin"):
            raise ValueError("Role must be 'user' or 'admin'.")
        if self.get_user(username):
            raise ValueError("Username already exists.")

        conn = self._connect()
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, hash_password(password), role),
            )
            conn.commit()
        finally:
            conn.close()

    def authenticate(self, username: str, password: str) -> bool:
        user = self.get_user(username)
        if not user:
            return False
        return verify_password(password, user["password_hash"])

    def change_password(self, username: str, new_password: str):
        if not new_password:
            raise ValueError("Password cannot be empty.")
        if not self.get_user(username):
            raise ValueError("User does not exist.")
        conn = self._connect()
        try:
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE username = ?",
                (hash_password(new_password), username),
            )
            conn.commit()
        finally:
            conn.close()

    def reset_password(self, target_username: str, new_password: str):
        self.change_password(target_username, new_password)

    def delete_user(self, target_username: str):
        if not self.get_user(target_username):
            raise ValueError("User does not exist.")
        if self.is_last_admin(target_username):
            raise ValueError("Cannot delete the last admin account.")
        conn = self._connect()
        try:
            conn.execute("DELETE FROM users WHERE username = ?", (target_username,))
            conn.commit()
        finally:
            conn.close()

    def is_admin(self, username: str) -> bool:
        user = self.get_user(username)
        return bool(user and user.get("role") == "admin")

    def is_last_admin(self, username: str) -> bool:
        user = self.get_user(username)
        if not user or user.get("role") != "admin":
            return False
        conn = self._connect()
        try:
            cur = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            count = cur.fetchone()[0]
            return count == 1
        finally:
            conn.close()

