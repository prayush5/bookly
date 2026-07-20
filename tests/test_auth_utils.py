from datetime import timedelta
import jwt
from datetime import timedelta
from src.auth.utils import create_token
from src.config import Config

from src.auth.utils import create_token, decode_token, generate_passwd_hash, verify_password


def test_password_hash_verifies_original_password():
    password = "strong-password"

    password_hash = generate_passwd_hash(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True
    assert verify_password("wrong-password", password_hash) is False


def test_created_token_can_be_decoded():
    user_data = {
        "email": "reader@example.com",
        "user_uid": "123",
        "role": "user",
    }

    token = create_token(
        user_data=user_data,
        expiry=timedelta(minutes=5),
    )
    payload = decode_token(token)

    assert payload is not None
    assert payload["user"] == user_data
    assert payload["refresh"] is False
    assert "jti" in payload


def test_decode_token_returns_none_for_invalid_token():
    assert decode_token("not-a-valid-token") is None

def test_create_access_token():
    user_data = {
        "user_uid": 1,
        "username": "John"
    }

    token = create_token(user_data)

    decoded = jwt.decode(
        token,
        Config.JWT_SECRET,
        algorithms=[Config.JWT_ALGORITHM]
    )

    assert decoded["user"] == user_data
    assert decoded["refresh"] is False
    assert decoded["purpose"] == "access"
    assert "jti" in decoded
    assert "exp" in decoded

def test_create_refresh_token():
    user_data = {
        "id": 1
    }

    token = create_token(
        user_data,
        expiry=timedelta(days=7),
        refresh=True,
        purpose="refresh"
    )

    decoded = jwt.decode(
        token,
        Config.JWT_SECRET,
        algorithms=[Config.JWT_ALGORITHM]
    )

    assert decoded["user"] == user_data
    assert decoded["refresh"] is True
    assert decoded["purpose"] == "refresh"