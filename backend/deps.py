from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import get_db
from .security import decode_token, verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


DBSession = Annotated[Session, Depends(get_db)]


def authenticate_user(
    db: DBSession, username: str, password: str
) -> Optional[models.User]:
    user = crud.get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(
    db: DBSession,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(sub=username, roles=payload.get("roles", []))
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_username(db, username=token_data.sub or "")
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: Annotated[models.User, Depends(get_current_user)]
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def role_required(min_level: int):
    def dependency(
        current_user: Annotated[models.User, Depends(get_current_active_user)]
    ) -> models.User:
        if current_user.max_role_level() < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough privileges",
            )
        return current_user

    return dependency


