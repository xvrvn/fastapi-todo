# src/auth/utils.py
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

import aiosmtplib
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import auth_settings
from .constants import ALGORITHM, PASSWORD_RESET_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# Password helpers
def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# JWT helpers
def create_access_token(
    data: dict, expires_delta: timedelta | None = None, secret_key: str | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(
            minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    key = secret_key or auth_settings.SECRET_KEY
    return jwt.encode(to_encode, key, algorithm=ALGORITHM)


def decode_token(token: str, secret_key: str | None = None) -> dict:
    key = secret_key or auth_settings.SECRET_KEY
    try:
        payload = jwt.decode(token, key, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise e


# Password reset token
def create_password_reset_token(email: str) -> str:
    return create_access_token(
        {"sub": email, "type": "password_reset"},
        expires_delta=timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
    )


def verify_password_reset_token(token: str) -> str:
    payload = decode_token(token)
    if payload.get("type") != "password_reset":
        raise JWTError("Invalid token type")
    email = payload.get("sub")
    if not email:
        raise JWTError("Invalid token payload")
    return email


# Async email sender
async def send_email(subject: str, to_email: str, body: str):
    if not all(
        [
            auth_settings.SMTP_SERVER,
            auth_settings.SMTP_PORT,
            auth_settings.SMTP_USER,
            auth_settings.SMTP_PASSWORD,
            auth_settings.FROM_EMAIL,
        ]
    ):
        raise RuntimeError(
            "SMTP is not configured. Set SMTP_SERVER/PORT/USER/PASSWORD/FROM_EMAIL in env."
        )
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = str(auth_settings.FROM_EMAIL)
    msg["To"] = to_email
    msg.set_content(body)

    await aiosmtplib.send(
        msg,
        hostname=auth_settings.SMTP_SERVER,
        port=int(auth_settings.SMTP_PORT),  # type: ignore
        start_tls=True,
        username=auth_settings.SMTP_USER,
        password=auth_settings.SMTP_PASSWORD,
    )
