import hashlib
import secrets
from typing import Optional

import database as db


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    key  = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return f"{salt}:{key.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, key = stored.split(":")
        check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
        return secrets.compare_digest(check.hex(), key)
    except Exception:
        return False


def generate_token() -> str:
    return secrets.token_hex(32)


def get_current_user(token: Optional[str]) -> Optional[dict]:
    if not token:
        return None
    return db.get_user_by_token(token)
