import base64
import uuid
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlmodel import col

import settings
from src.db.exceptions import ResourceAlreadyExists
from src.server.constants import FittingCreate
from src.db.base_manager import BaseDbManager
from src.db.projects.models import (
    Fitting,
    ProjectBase,
    Project,
    UserRole,
    RoleTypeOption,
    UserRoleBase,
    ProjectFitting,
    DeviceBase,
    Device,
    DxfFileBase,
    DxfFile,
)
from src.server.projects.models import ProjectExtendedWithIds


class ProjectsDbManager(BaseDbManager):
    async def create_fittins(
        self, session: AsyncSession, fittings: list[FittingCreate]
    ) -> list[Fitting]:
        objects = []
        for fitting in fittings:
            with open(settings.BASE_DIR / "data" / fitting.image_path, "rb") as img:
                img_str = base64.b64encode(img.read()).decode("utf-8")
            objects.append(
                Fitting(
                    name=fitting.name, groupname=fitting.groupname, image_b64=img_str
                )
            )
        session.add_all(objects)
        return objects

    async def get_all_fittings(self, session: AsyncSession) -> list[Fitting]:
        stmt = select(Fitting)
        fittings = (await session.execute(stmt)).scalars().all()
        return fittings

    async def get_fittings(
        self, session: AsyncSession, fittings_ids: set[uuid.UUID]
    ) -> list[Fitting]:
        stmt = select(Fitting).where(col(Fitting.id).in_(fittings_ids))
        tags = (await session.execute(stmt)).scalars().all()
        not_existing_tags_ids = set(fittings_ids) - set([t.id for t in tags])
        if len(not_existing_tags_ids) != 0:
            raise NoResultFound(
                f"Fittings with ids {not_existing_tags_ids} were not found in the DB"
            )
        return tags

    async def create_project(
        self, session: AsyncSession, project: ProjectBase, user_id: uuid.UUID
    ) -> Project:
        # Checking if user with this id exists should be done explicitly

        new_project = Project.parse_obj(project)
        session.add(new_project)

        new_user_role = UserRole(
            user_id=user_id, project_id=new_project.id, role_type=RoleTypeOption.author
        )
        session.add(new_user_role)

        return new_project

    async def get_project(
        self, session: AsyncSession, project_id: uuid.UUID
    ) -> ProjectExtendedWithIds:
        project = await Project.by_id(session, project_id)
        stmt = select(UserRole).where(UserRole.project_id == project_id)
        user_roles: list[UserRole] = (await session.execute(stmt)).scalars().all()
        assert (
            len(user_roles) == 2
        ), "Number of user roles should be exactly equal to two"
        if user_roles[0].role_type == RoleTypeOption.author:
            author_id = user_roles[0].user_id
            worker_id = user_roles[1].user_id
        else:
            author_id = user_roles[1].user_id
            worker_id = user_roles[0].user_id
        proj = ProjectExtendedWithIds(
            author_id=author_id, worker_id=worker_id, **project.dict()
        )
        return proj

    async def get_all_projects(
        self, session: AsyncSession
    ) -> list[ProjectExtendedWithIds]:
        stmt = select(UserRole)
        user_roles: list[UserRole] = (await session.execute(stmt)).scalars().all()
        author_id_by_project_id: dict[uuid.UUID, uuid.UUID] = dict()
        worker_id_by_project_id: dict[uuid.UUID, uuid.UUID] = dict()
        for ur in user_roles:
            if ur.role_type == RoleTypeOption.author:
                author_id_by_project_id[ur.project_id] = ur.user_id
            elif ur.role_type == RoleTypeOption.worker:
                worker_id_by_project_id[ur.project_id] = ur.user_id

        stmt = select(Project)
        projects = (await session.execute(stmt)).scalars().all()

        result = []
        for project in projects:
            proj = ProjectExtendedWithIds(
                author_id=author_id_by_project_id[project.id],
                worker_id=worker_id_by_project_id[project.id],
                **project.dict(),
            )
            result.append(proj)

        return result

    async def get_user_roles(
        self,
        session: AsyncSession,
        *,
        user_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        role_type: Optional[RoleTypeOption] = None,
    ) -> list[UserRole]:
        assert (
            user_id is not None or project_id is not None
        ), "Either user_id or project_id should not be None"

        stmt = select(UserRole)

        if user_id is not None:
            # Checking if user with this id exists should be done explicitly
            # await User.by_id(session, user_id)
            stmt = stmt.where(UserRole.user_id == user_id)
        if project_id is not None:
            # Checking if project with this id exists
            await Project.by_id(session, project_id)
            stmt = stmt.where(UserRole.project_id == project_id)
        if role_type is not None:
            stmt = stmt.where(UserRole.role_type == role_type)

        stmt = stmt.options(selectinload(UserRole.project))
        # stmt = stmt.options(selectinload(UserRole.user), selectinload(UserRole.project))

        return (await session.execute(stmt)).scalars().all()

    async def create_user_role(
        self, session: AsyncSession, user_role: UserRoleBase
    ) -> UserRole:
        # Checking if user with this id exists should be done explicitly

        # Checking if project with this id exists
        await Project.by_id(session, user_role.project_id)

        existing_user_role = (
            await session.execute(
                select(UserRole)
                .where(UserRole.role_type == user_role.role_type)
                .where(UserRole.user_id == user_role.user_id)
                .where(UserRole.project_id == user_role.project_id)
            )
        ).scalar_one_or_none()
        if existing_user_role is None:
            created_user_role = await UserRole.create(session, user_role)
            return created_user_role
        else:
            raise ResourceAlreadyExists(
                f"User role with role_type {user_role.role_type}, "
                f"user_id {user_role.user_id} and "
                f"project_id {user_role.project_id} already exists"
            )

    async def create_project_fittings(
        self, session: AsyncSession, project_id: uuid.UUID, fittings_ids: set[uuid.UUID]
    ) -> list[ProjectFitting]:
        """
        Will add new project fittings. If some already exist it'll be OK
        :returns newly created project fittings
        """
        await Project.by_id(session, project_id)
        await self.get_fittings(session, fittings_ids)

        # TODO: implement it with upsert with on conflict update updated_at field only
        stmt = select(ProjectFitting.fitting_id).where(
            ProjectFitting.project_id == project_id
        )
        current_project_fittings_ids: set[uuid.UUID] = set(
            (await session.execute(stmt)).scalars().all()
        )
        new_fittings_ids = set(fittings_ids) - current_project_fittings_ids

        new_project_fittings = [
            ProjectFitting(project_id=project_id, fitting_id=fitting_id)
            for fitting_id in new_fittings_ids
        ]
        session.add_all(new_project_fittings)
        return new_project_fittings

    async def get_fittings_by_project(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
    ) -> list[Fitting]:
        await Project.by_id(session, project_id)
        stmt = (
            select(ProjectFitting)
            .where(ProjectFitting.project_id == project_id)
            .options(selectinload(ProjectFitting.fitting))
        )
        project_fittings: list[ProjectFitting] = (
            (await session.execute(stmt)).scalars().all()
        )
        fittings = [pf.fitting for pf in project_fittings]

        return fittings

    async def create_devices(self, session: AsyncSession, devices: list[DeviceBase]):
        projects_ids = {d.project_id for d in devices}
        for project_id in projects_ids:
            await Project.by_id(session, project_id)

        new_devices = [Device.parse_obj(d) for d in devices]

        session.add_all(new_devices)

        return new_devices

    async def create_dxf_file(
        self, session: AsyncSession, dxf_file: DxfFileBase
    ) -> DxfFile:
        await Project.by_id(session, dxf_file.project_id)
        file = DxfFile.parse_obj(dxf_file)
        session.add(file)

        return file

    async def get_latest_dxf_file(
        self, session: AsyncSession, project_id: uuid.UUID
    ) -> DxfFile:
        await Project.by_id(session, project_id)

        stmt = (
            select(DxfFile)
            .where(DxfFile.project_id == project_id)
            .order_by(desc(DxfFile.created_at))
            .limit(1)
        )
        files = (await session.execute(stmt)).scalars().all()

        if len(files) == 0:
            raise NoResultFound("No DXF files found for this project")

        return files[0]
