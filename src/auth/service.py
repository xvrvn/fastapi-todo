from datetime import timedelta

from sqlmodel import Session, select

from .config import auth_settings
from .exceptions import BadRequest, UserAlreadyExists, UserNotFound
from .models import User
from .utils import (
    create_access_token,
    create_password_reset_token,
    hash_password,
    send_email,
    verify_password,
    verify_password_reset_token,
)


# ---- User creation / retrieval ----
def create_user(session: Session, email: str, password: str) -> User:
    statement = select(User).where(User.email == email)
    result = session.exec(statement).first()
    if result:
        raise UserAlreadyExists
    hashed = hash_password(password)
    user = User(email=email, hashed_password=hashed)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(session, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# ---- Token creation ----
def create_user_token(user: User, expires_minutes: int | None = None) -> str:
    data = {"sub": user.email}
    if expires_minutes:
        return create_access_token(
            data, expires_delta=timedelta(minutes=expires_minutes)
        )
    return create_access_token(data)


# ---- Password reset flow ----
def send_password_reset_email(session: Session, email: str, reset_base_url: str):
    user = get_user_by_email(session, email)
    if not user:
        # dev
        raise UserNotFound
    token = create_password_reset_token(email)
    link = f"{reset_base_url}?token={token}"
    subject = "Todo App - Password reset"
    body = f"Hi,\n\nClick the link below to reset your password. The link expires in {auth_settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES if hasattr(auth_settings, 'PASSWORD_RESET_TOKEN_EXPIRE_MINUTES') else 15} minutes.\n\n{link}\n\nIf you didn't ask for this, ignore this email."
    send_email(subject, email, body)
    return {"msg": "reset email sent"}


def reset_password(session: Session, token: str, new_password: str):
    try:
        email = verify_password_reset_token(token)
    except Exception:
        raise BadRequest("Invalid or expired token.") from Exception
    user = get_user_by_email(session, email)
    if not user:
        raise UserNotFound
    user.hashed_password = hash_password(new_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
