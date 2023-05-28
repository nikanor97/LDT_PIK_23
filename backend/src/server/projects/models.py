import uuid
from _decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from src.db.projects.models import ProjectBase, DeviceTypeOption


# class FittingCreate(BaseModel):
#     image_path: str
#     name: str
#     groupname: str


class ProjectCreate(ProjectBase):
    fittings_ids: list[uuid.UUID]  # ids of Fittings
    worker_id: uuid.UUID
    # workers_ids: list[
    #     uuid.UUID
    # ]  # ids of verificator users that will be attached to the project


class ProjectExtendedWithIds(ProjectBase):
    id: uuid.UUID
    author_id: uuid.UUID
    worker_id: uuid.UUID


class ProjectExtendedWithNames(ProjectBase):
    id: uuid.UUID
    author_name: str
    worker_name: str


class FittingRead(BaseModel):
    image: str
    name: str
    id: uuid.UUID


class FittingGroupRead(BaseModel):
    groupname: str
    values: list[FittingRead]


class DeviceRead(BaseModel):
    name: str
    type: DeviceTypeOption
    coord_x: Optional[Decimal]
    coord_y: Optional[Decimal]
    coord_z: Optional[Decimal]


class DxfFileWithDevices(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    type: str
    devices: list[DeviceRead]
