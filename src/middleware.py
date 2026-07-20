from slowapi import Limiter
from fastapi import Request
from slowapi.util import get_remote_address
import jwt

REDIS_URL="redis://localhost:6379/0"

def get_user_jwt(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            user_uid = payload.get("user", {}).get("user_uid")
            if user_uid:
                return f"user:{user_uid}"
        except Exception:
            pass
    
    return get_remote_address(request)

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=REDIS_URL
)

