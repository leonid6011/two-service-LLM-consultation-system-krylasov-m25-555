import pytest
import jwt as pyjwt

from app.core.config import settings
from app.core.jwt import decode_and_validate


def make_token(sub: str = "42", role: str = "user") -> str:
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=30)).timestamp()),
    }
    return pyjwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def test_decode_and_validate_success():
    token = make_token(sub="42", role="user")
    payload = decode_and_validate(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "user"


def test_decode_and_validate_invalid_token():
    with pytest.raises(ValueError, match="Invalid token"):
        decode_and_validate("garbage.not.a.token")


def test_decode_and_validate_expired_token():
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "42",
        "role": "user",
        "iat": int((now - timedelta(hours=2)).timestamp()),
        "exp": int((now - timedelta(hours=1)).timestamp()),
    }
    token = pyjwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    with pytest.raises(ValueError, match="expired"):
        decode_and_validate(token)
