# src/auth/dependencies.py
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session
from .exceptions import CredentialsException, UserNotFound
from .models import User
from .utils import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


GetSession = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
) -> User:
    try:
        payload = decode_token(token)
        email: str = payload.get("sub")  # type: ignore
        if email is None:
            raise CredentialsException
    except JWTError as err:
        raise CredentialsException from err
    statement = select(User).where(User.email == email)
    result = await session.exec(statement)
    user = result.first()
    if user is None:
        raise UserNotFound
    return user
