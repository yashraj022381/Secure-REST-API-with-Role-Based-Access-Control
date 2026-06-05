import secrets
from datetime import datetime, timezone, timedelta

verification_tokens = {}

def generate_verification_token(user_id: int) -> str:
    """Create a one-time token valid for 24 hours."""
    token = secrets.token_urlsafe(32)
    verification_tokens[token] = {
        "user_id": user_id,
        "expires": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    return token

def verify_token(token: str):
    """Check if token is valid and not expired."""
    data = verification_tokens.get(token)
    if not data:
        return None
    if datetime.now(timezone.utc) > data["expires"]:
        del verification_tokens[token]
        return None
    user_id = data["user_id"]
    del verification_tokens[token]  # one-time use
    return user_id
