import uuid

from pydantic import BaseModel

from src.db.projects.models import ProjectBase, DxfFileBase, Device


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


class DxfFileWithDevices(DxfFileBase):
    id: uuid.UUID
    devices: list[Device]
