from typing import List

from fastapi import APIRouter, Depends

from . import crud, models, schemas
from .deps import DBSession, role_required

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/roles", response_model=List[schemas.RoleRead])
def list_roles(
    db: DBSession,
    _: models.User = Depends(role_required(3)),
):
    return crud.get_roles(db)


@router.get("/logs", response_model=List[schemas.AuditLogRead])
def list_logs(
    db: DBSession,
    _: models.User = Depends(role_required(3)),
    skip: int = 0,
    limit: int = 100,
):
    from sqlalchemy import select

    stmt = (
        select(models.AuditLog)
        .order_by(models.AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


