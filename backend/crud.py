from typing import Iterable, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .security import get_password_hash


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    stmt = select(models.User).where(models.User.username == username)
    return db.scalars(stmt).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    stmt = select(models.User).where(models.User.email == email)
    return db.scalars(stmt).first()


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    stmt = select(models.User).where(models.User.id == user_id)
    return db.scalars(stmt).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    stmt = select(models.User).offset(skip).limit(limit)
    # из-за eager-load связи roles возможны дубликаты, поэтому вызываем unique()
    return list(db.scalars(stmt).unique().all())


def get_role_by_name(db: Session, name: str) -> Optional[models.Role]:
    stmt = select(models.Role).where(models.Role.name == name)
    return db.scalars(stmt).first()


def get_roles(db: Session) -> List[models.Role]:
    stmt = select(models.Role)
    return list(db.scalars(stmt).all())


def create_user(db: Session, username: str, email: str, password: str) -> models.User:
    hashed_password = get_password_hash(password)
    db_user = models.User(
        username=username,
        email=email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def set_user_roles(
    db: Session, user: models.User, role_names: Iterable[str]
) -> models.User:
    roles: list[models.Role] = []
    for role_name in role_names:
        role = get_role_by_name(db, role_name)
        if role:
            roles.append(role)
    user.roles = roles
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def log_action(
    db: Session,
    action: str,
    user: Optional[models.User] = None,
    details: Optional[str] = None,
) -> models.AuditLog:
    log_entry = models.AuditLog(
        user_id=user.id if user else None,
        action=action,
        details=details,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


