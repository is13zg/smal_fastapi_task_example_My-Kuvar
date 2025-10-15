from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from config import settings
from uuid import uuid4

crypto_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def make_hash(plain: str) -> str:
    return crypto_context.hash(plain)


def check_hash(plain: str, hashed: str) -> bool:
    return crypto_context.verify(plain, hashed)


def gen_token(user_id: int) -> str:
    now = datetime.now()
    payload = {
        "sub": str(user_id),
        "jti": str(uuid4()),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
    }
    token = jwt.encode(payload, settings.SECRET_KEY.get_secret_value(), algorithm=settings.ALGORITHM)
    return token


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY.get_secret_value(), algorithms=[settings.ALGORITHM])
