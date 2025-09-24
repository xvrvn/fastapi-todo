from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.database import get_session

DBSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
