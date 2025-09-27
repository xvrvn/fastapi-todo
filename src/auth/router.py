# src/auth/router.py
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session
from . import schemas, service
from .dependencies import get_current_user

router = APIRouter()


@router.post(
    "/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED
)
async def register(
    user_in: schemas.UserCreate, session: Annotated[AsyncSession, Depends(get_session)]
):
    user = await service.create_user(session, user_in.email, user_in.password)
    return user


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    user = await service.authenticate_user(
        session, form_data.username, form_data.password
    )
    if not user:
        from .exceptions import CredentialsException

        raise CredentialsException
    access_token = service.create_user_token(user)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserRead)
async def read_current_user(
    current_user: Annotated[schemas.UserRead, Depends(get_current_user)],
):
    return current_user


@router.post("/password-reset-request")
async def password_reset_request(
    payload: schemas.PasswordResetRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    reset_base = "http://localhost:3000/reset-password"
    return await service.send_password_reset_email(session, payload.email, reset_base)


@router.post("/password-reset-confirm")
async def password_reset_confirm(
    payload: schemas.PasswordResetConfirm,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    user = await service.reset_password(session, payload.token, payload.new_password)
    return {
        "msg": "password reset successful",
        "user": {"id": user.id, "email": user.email},
    }
