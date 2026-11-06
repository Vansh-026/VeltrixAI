
import sqlite3
import bcrypt
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "users.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)

def init_session_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                token_hash TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

def register_user(username, password):
    username = username.strip().lower()

    if not username or len(password) < 12:
        return False, "Enter a username and a password of at least 12 characters."

    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hashed)
            )
        return True, "Registration successful."
    except sqlite3.IntegrityError:
        return False, "Username already exists."


def login_user(username, password):
    username = username.strip().lower()

    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,)
        ).fetchone()

    if row and bcrypt.checkpw(
        password.encode("utf-8"),
        row[2].encode("utf-8")
    ):
        return {"id": row[0], "username": row[1]}

    return None
