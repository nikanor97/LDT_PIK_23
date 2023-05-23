import enum
import uuid
from datetime import datetime
from typing import Optional, TypeVar

import sqlalchemy
from sqlalchemy import Column, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlmodel import Field, Relationship
from src.db.common_sql_model import CommonSqlModel
from src.db.mixins import TimeStampWithIdMixin

UsersBase = declarative_base()

user_sqlmodel_T = TypeVar("user_sqlmodel_T", bound="UsersSQLModel")


class UsersSQLModel(CommonSqlModel):
    ...


UsersSQLModel.metadata = UsersBase.metadata  # type: ignore


class RoleTypeOption(str, enum.Enum):
    author = "author"
    view_only = "view_only"
    verificator = "verificator"


class TokenKindOption(str, enum.Enum):
    access = "access"
    refresh = "refresh"


class ProjectBase(UsersSQLModel):
    name: str = Field(nullable=False, index=True)
    description: Optional[str] = Field(nullable=True, default=None)


class Project(ProjectBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "projects"
    roles: list["UserRole"] = Relationship(
        back_populates="project", sa_relationship_kwargs={"lazy": "selectin"}
    )


class UserBase(UsersSQLModel):
    name: str = Field(nullable=False, index=True)
    email: str = Field(nullable=False, index=True, unique=True)


class User(UserBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "users"
    roles: list["UserRole"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )


class UserRoleBase(UsersSQLModel):
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id", index=True)

    role_type: RoleTypeOption = Field(
        sa_column=Column(sqlalchemy.Enum(RoleTypeOption), nullable=False)
    )


class UserRole(UserRoleBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "user_roles"
    __table_args__ = (
        Index(
            "idx_user_project_role", "user_id", "project_id", "role_type", unique=True
        ),
    )

    user: User = Relationship(
        back_populates="roles", sa_relationship_kwargs={"lazy": "selectin"}
    )
    project: Project = Relationship(
        back_populates="roles", sa_relationship_kwargs={"lazy": "selectin"}
    )


class UserTokenBase(UsersSQLModel):
    access_token: str = Field(nullable=False)
    refresh_token: str = Field(nullable=False)
    token_type: str = Field(nullable=True)
    access_expires_at: datetime = Field(nullable=False)
    refresh_expires_at: datetime = Field(nullable=False)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    is_valid: bool = Field(nullable=False, default=True)


class UserToken(UserTokenBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "user_tokens"
    user: User = Relationship(sa_relationship_kwargs={"lazy": "selectin"})


class UserPassword(UsersSQLModel, TimeStampWithIdMixin, table=True):
    __tablename__ = "user_passwords"
    hashed_password: str = Field(nullable=False)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
