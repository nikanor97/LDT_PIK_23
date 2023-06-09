import enum
import uuid
from _decimal import Decimal
from datetime import datetime
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
    created_at: datetime


class ProjectExtendedWithNames(ProjectBase):
    id: uuid.UUID
    author_name: str
    worker_name: str
    created_at: datetime


class FittingRead(BaseModel):
    image: str
    name: str
    id: uuid.UUID


class FittingGroupRead(BaseModel):
    groupname: str
    values: list[FittingRead]


class DeviceRead(BaseModel):
    id: uuid.UUID
    type_human: str
    type: DeviceTypeOption
    coord_x: Optional[Decimal]
    coord_y: Optional[Decimal]
    coord_z: Optional[Decimal]


class DxfFileWithDevices(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    type: str
    devices: list[DeviceRead]
    image: str


class DeviceTypeWithCoords(BaseModel):
    id: uuid.UUID
    type: DeviceTypeOption
    coord_x: float
    coord_y: float
    coord_z: float


class DevicesWithHeights(BaseModel):
    dxf_file_id: uuid.UUID
    project_id: uuid.UUID
    devices: list[DeviceTypeWithCoords]


class ConnectionPoint(BaseModel):
    id: uuid.UUID
    # order: str
    type: str
    diameter: Decimal
    coord_x: Decimal
    coord_y: Decimal
    coord_z: Decimal


class ProjectResultConnectionPoints(BaseModel):
    tab_name: str
    table: list[ConnectionPoint]
    image: str


class GraphVertex(BaseModel):
    id: uuid.UUID
    graph: str
    material: str
    # probability: Decimal


class ProjectResultGraph(BaseModel):
    tab_name: str
    table: list[GraphVertex]
    image: str


class FittingStat(BaseModel):
    name: str
    material_id: str
    n_items: int
    total_length: Optional[int]


class ProjectResultFittingsStat(BaseModel):
    tab_name: str
    table: list[FittingStat]
    image: str


class ProjectResult(BaseModel):
    fittings_stat: ProjectResultFittingsStat
    connection_points: ProjectResultConnectionPoints
    graph: ProjectResultGraph


class ProjectSewerVariant(BaseModel):
    variant_num: int
    result: ProjectResult
    n_fittings: int
    sewer_length: Decimal


class ProjectWithResults(ProjectExtendedWithNames):
    results: Optional[list[ProjectSewerVariant]]


class ExportFileType(str, enum.Enum):
    excel = "excel"
    stl = "stl"
    png = "png"


class ProjectsDelete(BaseModel):
    project_ids: list[uuid.UUID]


class DeviceStats(BaseModel):
    type_human: str
    n_occur: int


class ProjectsStats(BaseModel):
    avg_n_fittings: Decimal
    avg_sewer_length: Decimal
    devices: list[DeviceStats]
