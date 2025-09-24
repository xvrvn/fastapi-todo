from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from ..database import get_session
from . import dependencies, schemas, service

router = APIRouter()


# POST /auth/register
@router.post(
    "/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED
)
def register(
    user_in: schemas.UserCreate, session: Annotated[Session, Depends(get_session)]
):
    user = service.create_user(session, user_in.email, user_in.password)
    return user


# POST /auth/token  (OAuth2 access token)
@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends()],
):
    user = service.authenticate_user(session, form_data.username, form_data.password)
    if not user:
        from .exceptions import CredentialsException

        raise CredentialsException
    access_token = service.create_user_token(user)
    return {"access_token": access_token, "token_type": "bearer"}


# GET /auth/me
@router.get("/me", response_model=schemas.UserRead)
def read_current_user(
    current_user: Annotated[schemas.UserRead, Depends(dependencies.get_current_user)],
):
    return current_user


# POST /auth/password-reset-request
@router.post("/password-reset-request")
def password_reset_request(
    payload: schemas.PasswordResetRequest, session: Annotated[Session, Depends()]
):
    # front-end should provide base url to build link, but to avoid exposing we accept env or fallback
    reset_base = "http://localhost:3000/reset-password"  # front-end page; in prod pass from frontend
    return service.send_password_reset_email(session, payload.email, reset_base)


# POST /auth/password-reset-confirm
@router.post("/password-reset-confirm")
def password_reset_confirm(
    payload: schemas.PasswordResetConfirm, session: Annotated[Session, Depends()]
):
    user = service.reset_password(session, payload.token, payload.new_password)
    return {
        "msg": "password reset successful",
        "user": {"id": user.id, "email": user.email},
    }
