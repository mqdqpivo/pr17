from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class RoleBase(BaseModel):
    name: str
    level: int


class RoleRead(RoleBase):
    id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)


class UserCreateByAdmin(UserBase):
    password: str = Field(min_length=8, max_length=128)
    roles: List[str] = []


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    roles: List[RoleRead] = []

    class Config:
        from_attributes = True


class UserUpdateProfile(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None
    roles: List[str] = []
    exp: Optional[int] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class AssignRolesRequest(BaseModel):
    roles: List[str]


class AuditLogRead(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    details: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


