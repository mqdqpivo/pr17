from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .config import settings
from .database import get_db
from .deps import DBSession, authenticate_user, get_current_active_user
from .security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.Token)
def register(user_in: schemas.UserCreate, db: DBSession):
    if user_in.password != user_in.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )
    if crud.get_user_by_username(db, user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    if crud.get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = crud.create_user(
        db, username=user_in.username, email=user_in.email, password=user_in.password
    )

    # По умолчанию присваиваем роль "user", если она есть
    default_role = crud.get_role_by_name(db, "user")
    if default_role:
        user.roles.append(default_role)
        db.add(user)
        db.commit()
        db.refresh(user)

    crud.log_action(db, "register", user=user, details="User self-registered")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    roles = [role.name for role in user.roles]
    access_token = create_access_token(
        subject=user.username,
        roles=roles,
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.Token)
def login(form_data: schemas.LoginRequest, db: DBSession):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        crud.log_action(
            db,
            "login_failed",
            user=None,
            details=f"Failed login for username={form_data.username}",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    roles = [role.name for role in user.roles]
    access_token = create_access_token(
        subject=user.username,
        roles=roles,
        expires_delta=access_token_expires,
    )
    crud.log_action(db, "login_success", user=user)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserRead)
def read_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user


