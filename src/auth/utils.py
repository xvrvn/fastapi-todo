import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import auth_settings
from .constants import ALGORITHM, PASSWORD_RESET_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Password helpers ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# --- JWT helpers ---
def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
    secret_key: str = None,  # type: ignore
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(
            minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    key = secret_key or auth_settings.SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, key, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str, secret_key: str = None):  # type: ignore
    key = secret_key or auth_settings.SECRET_KEY
    try:
        payload = jwt.decode(token, key, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise e


# --- Password reset token (short lived) ---
def create_password_reset_token(email: str):
    delta = timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        {"sub": email, "type": "password_reset"}, expires_delta=delta
    )


def verify_password_reset_token(token: str) -> str:
    payload = decode_token(token)
    # minimal validation
    token_type = payload.get("type")
    if token_type != "password_reset":
        raise JWTError("Invalid token type")
    email = payload.get("sub")
    if not email:
        raise JWTError("Invalid token payload")
    return email


# --- Email sending helper (simple SMTP) ---
def send_email(subject: str, to_email: str, body: str):
    if not all(
        [
            auth_settings.SMTP_SERVER,
            auth_settings.SMTP_PORT,
            auth_settings.SMTP_USER,
            auth_settings.SMTP_PASSWORD,
            auth_settings.FROM_EMAIL,
        ]
    ):
        # If SMTP not configured, raise or log. Here we'll raise for clarity.
        raise RuntimeError(
            "SMTP is not configured. Set SMTP_SERVER/PORT/USER/PASSWORD/FROM_EMAIL in env."
        )
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = str(auth_settings.FROM_EMAIL)
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(auth_settings.SMTP_SERVER, auth_settings.SMTP_PORT) as smtp:  # type: ignore
        smtp.starttls()
        smtp.login(auth_settings.SMTP_USER, auth_settings.SMTP_PASSWORD)  # type: ignore
        smtp.send_message(msg)
