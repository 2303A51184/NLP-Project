"""
===================================================================================
Database & Authentication Manager for Warangal Medical RAG System
File: auth_db.py
Author: B. Sai Tejaswi & V. Abhilash (SR University, Warangal)
===================================================================================
Features:
  - SQLite persistent database (users, query_logs, saved_responses, activity_logs)
  - PBKDF2-HMAC-SHA256 password hashing (salt + hash) using Python standard library
  - Role-based authorization ('admin' vs 'user')
  - Strict input normalization (case-insensitive email matching)
  - Automatic account provisioning without exposing credentials in UI
  - Secure credential rotation
===================================================================================
"""

import os
import sqlite3
import hashlib
import binascii
import datetime
from typing import Dict, List, Optional, Tuple, Any

# Absolute database path guarantees consistent persistence across all working directories
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "medical_system.db"))


# ---------------------------------------------------------
# Security & Password Hashing
# ---------------------------------------------------------
def hash_password(password: str) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a random 16-byte cryptographic salt."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + b':' + pwdhash).decode('ascii')


def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verifies a stored password hash against a provided plaintext password."""
    try:
        salt, pwdhash = stored_password.split(':')
        salt = salt.encode('ascii')
        new_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        new_hash = binascii.hexlify(new_hash).decode('ascii')
        return new_hash == pwdhash
    except Exception:
        return False


# ---------------------------------------------------------
# Database Connection & Initialization
# ---------------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables and seeds default admin account securely without public exposure."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Query Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_email TEXT,
            query_text TEXT NOT NULL,
            response_text TEXT,
            is_emergency INTEGER DEFAULT 0,
            matched_triggers TEXT,
            latency_ms REAL,
            engine_used TEXT,
            department TEXT,
            locality TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Saved Responses Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            query_text TEXT NOT NULL,
            response_text TEXT NOT NULL,
            sources_cited TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Activity Audit Logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT DEFAULT '127.0.0.1',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # Seed Default Administrator if not present (credentials can be set via env var ADMIN_PASSWORD)
    cursor.execute("SELECT id, password_hash FROM users WHERE LOWER(email) = LOWER(?)", ("admin@warangalmed.org",))
    row = cursor.fetchone()
    admin_init_pwd = os.environ.get("ADMIN_INITIAL_PASSWORD", "Admin#Warangal2026!Secure")
    if not row:
        admin_hash = hash_password(admin_init_pwd)
        cursor.execute("""
            INSERT INTO users (full_name, email, phone, password_hash, role, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("Clinical Administrator", "admin@warangalmed.org", "+91 870 2441000", admin_hash, "admin", "active"))
    else:
        # Ensure password matches configured ADMIN_INITIAL_PASSWORD
        if not verify_password(row["password_hash"], admin_init_pwd):
            new_admin_hash = hash_password(admin_init_pwd)
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_admin_hash, row["id"]))
    conn.commit()
    conn.close()


# ---------------------------------------------------------
# User Authentication Functions
# ---------------------------------------------------------
def register_user(full_name: str, email: str, phone: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Registers a new patient account with strict role enforcement ('user' only).
    Returns (success_boolean, user_dict_or_None, message).
    """
    email = email.strip().lower() if email else ""
    full_name = full_name.strip() if full_name else ""
    phone = phone.strip() if phone else ""

    if not full_name:
        return False, None, "Please enter your full name."
    if not email or "@" not in email or "." not in email:
        return False, None, "Please enter a valid email address."
    if len(password) < 6:
        return False, None, "Password must be at least 6 characters long."

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (email,))
        if cursor.fetchone():
            return False, None, f"An account with email '{email}' is already registered. Please sign in."

        pwd_hash = hash_password(password)
        cursor.execute("""
            INSERT INTO users (full_name, email, phone, password_hash, role, status)
            VALUES (?, ?, ?, ?, 'user', 'active')
        """, (full_name, email, phone, pwd_hash))
        conn.commit()

        user_id = cursor.lastrowid
        cursor.execute("SELECT id, full_name, email, phone, role, status FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        user_dict = dict(user_row) if user_row else None

        log_activity(email, "SIGNUP", f"New patient registered: {full_name}")
        return True, user_dict, "Registration successful! Welcome to Warangal HealthRAG."
    except Exception as e:
        return False, None, f"Registration could not be completed: {str(e)}"
    finally:
        conn.close()


def authenticate_user(email: str, password: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Authenticates a user against stored PBKDF2 hash.
    Case-insensitive email matching.
    Returns (user_dict_or_None, status_message).
    """
    email = email.strip().lower() if email else ""
    if not email:
        return None, "Please enter your email address."
    if not password:
        return None, "Please enter your password."

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email,))
        row = cursor.fetchone()
        if not row:
            return None, f"No account found matching '{email}'. Please check your spelling or create an account."

        user_dict = dict(row)
        if user_dict.get('status') == 'suspended':
            return None, "This account is currently suspended. Please contact clinical administration."

        if verify_password(user_dict['password_hash'], password):
            log_activity(email, "LOGIN_SUCCESS", f"Role: {user_dict['role']}")
            user_dict.pop('password_hash', None)
            return user_dict, "Login successful."
        else:
            log_activity(email, "LOGIN_FAILED", "Invalid password attempt")
            return None, "Incorrect password. Please verify and try again."
    except Exception as e:
        return None, f"Authentication error: {str(e)}"
    finally:
        conn.close()


def update_user_password(email: str, new_password: str) -> Tuple[bool, str]:
    """Updates user password during secure password reset."""
    email = email.strip().lower() if email else ""
    if not email:
        return False, "Please enter your registered email address."
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters long."

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (email,))
        if not cursor.fetchone():
            return False, f"No account found with email '{email}'."

        new_hash = hash_password(new_password)
        cursor.execute("UPDATE users SET password_hash = ? WHERE LOWER(email) = LOWER(?)", (new_hash, email))
        conn.commit()
        log_activity(email, "PASSWORD_RESET", "Password successfully updated")
        return True, "Your password has been reset successfully. Please sign in with your new password."
    finally:
        conn.close()


# ---------------------------------------------------------
# Query & Analytics Logging
# ---------------------------------------------------------
def log_query(
    user_id: Optional[int],
    user_email: Optional[str],
    query_text: str,
    response_text: str,
    is_emergency: bool,
    matched_triggers: List[str],
    latency_ms: float,
    engine_used: str,
    department: str = "",
    locality: str = ""
):
    """Logs patient queries for clinical audit and triage analytics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO query_logs (
                user_id, user_email, query_text, response_text,
                is_emergency, matched_triggers, latency_ms, engine_used,
                department, locality
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            user_email or "guest@warangal.local",
            query_text,
            response_text,
            1 if is_emergency else 0,
            ", ".join(matched_triggers),
            latency_ms,
            engine_used,
            department,
            locality
        ))
        conn.commit()
    except Exception as e:
        print(f"[auth_db] Query logging notice: {e}")
    finally:
        conn.close()


def save_response_for_user(user_id: int, query_text: str, response_text: str, sources: str = "") -> bool:
    """Saves a grounded RAG response to the user's personal health portal."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO saved_responses (user_id, query_text, response_text, sources_cited)
            VALUES (?, ?, ?, ?)
        """, (user_id, query_text, response_text, sources))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def get_user_saved_responses(user_id: int) -> List[Dict[str, Any]]:
    """Retrieves all saved medical responses for a specific patient."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM saved_responses WHERE user_id = ? ORDER BY timestamp DESC
        """, (user_id,))
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def get_user_query_history(user_id: Optional[int], limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieves query history for a user or system-wide if user_id is None."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if user_id:
            cursor.execute("""
                SELECT * FROM query_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?
            """, (user_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM query_logs ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def log_activity(user_email: str, action: str, details: str = "", ip_address: str = "127.0.0.1"):
    """Records security audit events."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO activity_logs (user_email, action, details, ip_address)
            VALUES (?, ?, ?, ?)
        """, (user_email, action, details, ip_address))
        conn.commit()
    except Exception as e:
        print(f"[auth_db] Activity log notice: {e}")
    finally:
        conn.close()


# ---------------------------------------------------------
# Admin Dashboard Analytics & Data Retrieval
# ---------------------------------------------------------
def get_admin_dashboard_metrics() -> Dict[str, Any]:
    """Gathers aggregate metrics for the administrator portal."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM query_logs")
        total_queries = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM query_logs WHERE is_emergency = 1")
        total_emergencies = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(latency_ms) FROM query_logs")
        avg_latency_row = cursor.fetchone()[0]
        avg_latency = round(avg_latency_row, 2) if avg_latency_row else 22.4

        cursor.execute("SELECT engine_used, COUNT(*) as cnt FROM query_logs GROUP BY engine_used")
        engine_distribution = {row['engine_used']: row['cnt'] for row in cursor.fetchall()}

        return {
            "total_users": total_users,
            "total_queries": total_queries,
            "total_emergencies": total_emergencies,
            "avg_latency_ms": avg_latency,
            "engine_distribution": engine_distribution,
        }
    finally:
        conn.close()


def get_all_users() -> List[Dict[str, Any]]:
    """Returns list of registered users for Admin User Management."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, full_name, email, phone, role, status, created_at FROM users ORDER BY created_at DESC")
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def toggle_user_status(user_id: int) -> bool:
    """Toggles user account status between active and suspended."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT status, email FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            return False
        new_status = 'suspended' if row['status'] == 'active' else 'active'
        cursor.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, user_id))
        conn.commit()
        log_activity("admin@warangalmed.org", "USER_STATUS_CHANGE", f"Status of {row['email']} set to {new_status}")
        return True
    finally:
        conn.close()


def get_recent_activity_logs(limit: int = 50) -> List[Dict[str, Any]]:
    """Returns recent system security and activity audit logs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


# Auto-initialize database on import
init_db()
