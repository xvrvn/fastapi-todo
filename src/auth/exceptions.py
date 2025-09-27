# src/auth/exceptions.py
from fastapi import HTTPException, status

CredentialsException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

UserAlreadyExists = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="User with this email already exists.",
)

UserNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found.",
)


def BadRequest(detail: str = "Bad request") -> HTTPException:
    return HTTPException(status_code=400, detail=detail)
