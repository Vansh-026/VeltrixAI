
import secrets
import hashlib
import time

from database import get_connection, init_session_table

SESSION_DURATION = 7 * 24 * 60 * 60


def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


def create_session(user_id):
    init_session_table()

    token = secrets.token_urlsafe(32)
    token_hash = hash_token(token)
    expires_at = int(time.time()) + SESSION_DURATION

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO user_sessions
            (token_hash, user_id, expires_at)
            VALUES (?, ?, ?)
            """,
            (token_hash, user_id, expires_at)
        )

    return token


def validate_session(token):
    init_session_table()

    token_hash = hash_token(token)

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT users.id, users.username
            FROM user_sessions
            JOIN users
            ON users.id = user_sessions.user_id
            WHERE token_hash = ?
            AND expires_at > ?
            """,
            (token_hash, int(time.time()))
        ).fetchone()

    if row:
        return {
            "id": row[0],
            "username": row[1]
        }

    return None


def revoke_session(token):
    if not token:
        return

    with get_connection() as conn:
        conn.execute(
            "DELETE FROM user_sessions WHERE token_hash = ?",
            (hash_token(token),)
        )
