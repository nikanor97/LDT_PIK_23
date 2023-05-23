import uuid

from pydantic import BaseModel

from src.db.users.models import Project, ProjectBase, User, UserRoleBase


class UserRoleWithProjectRead(UserRoleBase):
    id: uuid.UUID
    user: User
    project: Project


class ProjectCreate(ProjectBase):
    user_id: uuid.UUID


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenWithExpiryData(Token):
    access_expires_at: int  # n_seconds to expiry
    refresh_expires_at: int  # n_seconds to expiry
