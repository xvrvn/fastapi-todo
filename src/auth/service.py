# src/auth/service.py
from datetime import datetime, timedelta, timezone

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

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


# create user
async def create_user(session: AsyncSession, email: str, password: str) -> User:
    q = select(User).where(User.email == email)
    result = await session.exec(q)
    if result.first():
        raise UserAlreadyExists
    user = User(
        email=email,
        hashed_password=hash_password(password),
        is_active=True,
        created_at=datetime.now(timezone.utc),  # offset-aware
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# get by email
async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    q = select(User).where(User.email == email)
    result = await session.exec(q)
    return result.first()


# authenticate
async def authenticate_user(
    session: AsyncSession, email: str, password: str
) -> User | None:
    user = await get_user_by_email(session, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


# token creation
def create_user_token(user: User, expires_minutes: int | None = None) -> str:
    return create_access_token(
        {"sub": user.email},
        expires_delta=timedelta(minutes=expires_minutes) if expires_minutes else None,
    )


# password reset
async def send_password_reset_email(
    session: AsyncSession, email: str, reset_base_url: str
):
    user = await get_user_by_email(session, email)
    if not user:
        raise UserNotFound
    token = create_password_reset_token(email)
    link = f"{reset_base_url}?token={token}"
    subject = "Todo App - Password reset"
    body = f"Hi,\n\nClick the link below to reset your password. The link expires in {auth_settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes.\n\n{link}\n\nIf you didn't ask for this, ignore this email."
    await send_email(subject, email, body)
    return {"msg": "reset email sent"}


async def reset_password(session: AsyncSession, token: str, new_password: str):
    try:
        email = verify_password_reset_token(token)
    except Exception:
        raise BadRequest("Invalid or expired token.") from Exception
    user = await get_user_by_email(session, email)
    if not user:
        raise UserNotFound
    user.hashed_password = hash_password(new_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
