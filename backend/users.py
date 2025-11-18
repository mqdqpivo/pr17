from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from . import crud, models, schemas
from .deps import DBSession, get_current_active_user, role_required

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserRead)
def read_own_profile(current_user: models.User = Depends(get_current_active_user)):
    return current_user


@router.get("/", response_model=List[schemas.UserRead])
def list_users(
    db: DBSession,
    _: models.User = Depends(role_required(3)),  # администратор
    skip: int = 0,
    limit: int = 100,
):
    return crud.get_users(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user_by_admin(
    user_in: schemas.UserCreateByAdmin,
    db: DBSession,
    _: models.User = Depends(role_required(3)),
):
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
    crud.set_user_roles(db, user, user_in.roles)
    crud.log_action(db, "user_created_by_admin", user=user)
    return user


@router.put("/{user_id}/roles", response_model=schemas.UserRead)
def assign_roles(
    user_id: int,
    roles_in: schemas.AssignRolesRequest,
    db: DBSession,
    admin: models.User = Depends(role_required(3)),
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user = crud.set_user_roles(db, user, roles_in.roles)
    crud.log_action(
        db,
        "roles_changed",
        user=admin,
        details=f"Changed roles for user_id={user.id} to {roles_in.roles}",
    )
    return user


