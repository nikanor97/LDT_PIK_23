import enum
import uuid
from decimal import Decimal
from typing import Optional, TypeVar

import sqlalchemy
from sqlalchemy import Index, Column, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlmodel import Field, Relationship
from src.db.common_sql_model import CommonSqlModel
from src.db.mixins import TimeStampWithIdMixin

ProjectsBase = declarative_base()

projects_sqlmodel_T = TypeVar("projects_sqlmodel_T", bound="ProjectsSQLModel")


class ProjectsSQLModel(CommonSqlModel):
    ...


ProjectsSQLModel.metadata = ProjectsBase.metadata  # type: ignore
# TODO: add indexes


class RoleTypeOption(str, enum.Enum):
    author = "author"
    view_only = "view_only"
    worker = "worker"


# class ProjectStatusOption(str, enum.Enum):
#     created = "created"  # When project is created or sent to the building stage
#     in_progress = "ready"
#     error = "error"  # When the project is totally finished


class ProjectStatusOption(int, enum.Enum):
    created = 0  # When project is created, but no trace buildings initialised
    in_progress = 100  # When project is sent to the building stage
    ready = 200
    error = 400  # When the project is totally finished


class ProjectTypeOption(str, enum.Enum):
    dxf = "dxf"
    manual = "manual"


class DeviceTypeOption(str, enum.Enum):
    toilet = "toilet"
    bath = "bath"
    washing_machine = "washing_machine"
    sink = "sink"
    faucet = "faucet"
    kitchen_sink = "kitchen_sink"


device_type_to_name = {
    DeviceTypeOption.toilet: "Туалет",
    DeviceTypeOption.bath: "Ванна",
    DeviceTypeOption.washing_machine: "Стиральная машина",
    DeviceTypeOption.sink: "Раковина",
    DeviceTypeOption.faucet: "Кран",
    DeviceTypeOption.kitchen_sink: "Мойка кухня",
}


class ProjectBase(ProjectsSQLModel):
    name: str = Field(nullable=False, index=True)
    description: Optional[str] = Field(nullable=True, default=None)
    status: Optional[ProjectStatusOption] = Field(
        sa_column=Column(
            sqlalchemy.Enum(ProjectStatusOption), default=ProjectStatusOption.created
        )
    )
    type: ProjectTypeOption = Field(
        sa_column=Column(sqlalchemy.Enum(ProjectTypeOption))
    )
    bathroom_type: Optional[str] = Field(nullable=True)
    is_deleted: Optional[bool] = Field(default=False)
    dxf_file_id: Optional[uuid.UUID] = Field(nullable=True)  # ID of actual dxf file


class Project(ProjectBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "projects"
    roles: list["UserRole"] = Relationship(
        back_populates="project", sa_relationship_kwargs={"lazy": "selectin"}
    )
    dxf_file: Optional["DxfFile"] = Relationship(
        back_populates="project", sa_relationship_kwargs={"lazy": "selectin"}
    )
    sewer_variants: list["SewerVariant"] = Relationship(back_populates="project")


class UserRoleBase(ProjectsSQLModel):
    user_id: uuid.UUID = Field(nullable=False, index=True)
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

    project: Project = Relationship(
        back_populates="roles", sa_relationship_kwargs={"lazy": "selectin"}
    )


class FittingBase(ProjectsSQLModel):
    name: str
    groupname: str
    image_b64: str
    material_id: Optional[str]


class Fitting(FittingBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "fittings"


class DeviceBase(ProjectsSQLModel):
    dxf_file_id: uuid.UUID = Field(foreign_key="dxf_files.id")
    name: str = Field(nullable=False)
    type_human: str = Field(nullable=False)  # same sense as type
    type: DeviceTypeOption = Field(
        sa_column=Column(sqlalchemy.Enum(DeviceTypeOption), nullable=False)
    )
    coord_x: Optional[Decimal] = Field(nullable=True)
    coord_y: Optional[Decimal] = Field(nullable=True)
    coord_z: Optional[Decimal] = Field(nullable=True)


class Device(DeviceBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "devices"
    dxf_file: "DxfFile" = Relationship(
        back_populates="devices", sa_relationship_kwargs={"lazy": "selectin"}
    )


class DxfFileBase(ProjectsSQLModel):
    project_id: uuid.UUID = Field(foreign_key="projects.id")
    source_url: Optional[str] = Field(nullable=True)


class DxfFile(DxfFileBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "dxf_files"
    project: Project = Relationship(
        back_populates="dxf_file", sa_relationship_kwargs={"lazy": "selectin"}
    )
    devices: list[Device] = Relationship(back_populates="dxf_file")


class ProjectFitting(ProjectsSQLModel, TimeStampWithIdMixin, table=True):
    __tablename__ = "project_fittings"
    __table_args__ = (
        UniqueConstraint("project_id", "fitting_id", name="project_fitting_constr"),
    )
    project_id: uuid.UUID = Field(foreign_key="projects.id", index=True)
    fitting_id: uuid.UUID = Field(foreign_key="fittings.id", index=True)
    fitting: Fitting = Relationship(sa_relationship_kwargs={"lazy": "selectin"})
    project: Project = Relationship(sa_relationship_kwargs={"lazy": "selectin"})


class SewerVariantBase(ProjectsSQLModel):
    excel_source_url: str = Field(nullable=False)
    stl_source_url: str = Field(nullable=False)
    png_source_url: str = Field(nullable=False)
    variant_num: Optional[int] = Field(nullable=True)
    n_fittings: Optional[int] = Field(nullable=True)
    sewer_length: Optional[Decimal] = Field(nullable=True)


class SewerVariant(SewerVariantBase, TimeStampWithIdMixin, table=True):
    __tablename__ = "sewer_variants"
    project_id: uuid.UUID = Field(foreign_key="projects.id", index=True)

    project: Project = Relationship(back_populates="sewer_variants")
