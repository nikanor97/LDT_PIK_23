import base64
import uuid
from typing import Optional

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
    SewerVariant,
    SewerVariantBase,
    ProjectStatusOption,
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
                    name=fitting.name,
                    groupname=fitting.groupname,
                    image_b64=img_str,
                    material_id=fitting.material_id,
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

        stmt = select(Project).where(Project.is_deleted == False)
        projects = (await session.execute(stmt)).scalars().all()

        result: list[ProjectExtendedWithIds] = []
        for project in projects:
            proj = ProjectExtendedWithIds(
                author_id=author_id_by_project_id[project.id],
                worker_id=worker_id_by_project_id[project.id],
                **project.dict(),
            )
            result.append(proj)
        result = sorted(result, key=lambda x: x.created_at, reverse=True)

        return result

    async def delete_projects(
        self, session: AsyncSession, projects_ids: set[uuid.UUID]
    ):
        stmt = (
            select(Project)
            .where(Project.is_deleted == False)
            .where(col(Project.id).in_(projects_ids))
        )
        projects = (await session.execute(stmt)).scalars().all()
        not_found_projects_ids = set(projects_ids) - set([p.id for p in projects])
        if len(not_found_projects_ids) > 0:
            raise NoResultFound(
                f"Projects with ids {not_found_projects_ids} were not found"
            )

        for idx, project in enumerate(projects):
            projects[idx].is_deleted = True

        session.add_all(projects)
        return projects

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

    async def create_devices(
        self, session: AsyncSession, devices: list[DeviceBase]
    ) -> list[Device]:
        dxf_file_ids = {d.dxf_file_id for d in devices}
        for dxf_file_id in dxf_file_ids:
            await DxfFile.by_id(session, dxf_file_id)

        new_devices = [Device.parse_obj(d) for d in devices]

        session.add_all(new_devices)

        return new_devices

    async def update_devices_z_coord(
        self, session: AsyncSession, new_z_coords: dict[uuid.UUID, int]
    ) -> list[Device]:
        stmt = select(Device).where(col(Device.id).in_(new_z_coords.keys()))
        devices = (await session.execute(stmt)).scalars().all()
        updated_devices = []
        for device in devices:
            device.coord_z = new_z_coords[device.id]
            updated_devices.append(device)
        session.add_all(updated_devices)
        return updated_devices

    async def get_devices(
        self, session: AsyncSession, project_ids: set[uuid.UUID]
    ) -> list[Device]:
        # project = await Project.by_id(session, project_id)
        stmt = select(Project).where(col(Project.id).in_(set(project_ids)))
        projects: list[Project] = (await session.execute(stmt)).scalars().all()
        projects_ids_from_db = {p.id for p in projects}

        wrong_project_ids = set(project_ids) - set(projects_ids_from_db)
        if len(wrong_project_ids) > 0:
            raise NoResultFound(f"Projects with ids {wrong_project_ids} were not found")

        dxf_file_ids = {p.dxf_file_id for p in projects}

        # devices: list[Device] = []
        # if project.dxf_file_id is None:
        #     return devices
        # stmt = select(Device).where(Device.dxf_file_id == project.dxf_file_id)
        # devices: list[Device] = (await session.execute(stmt)).scalars().all()

        devices: list[Device] = []
        if len(dxf_file_ids) == 0:
            return devices
        stmt = select(Device).where(col(Device.dxf_file_id).in_(dxf_file_ids))
        devices: list[Device] = (await session.execute(stmt)).scalars().all()
        return devices

    async def create_dxf_file(
        self, session: AsyncSession, dxf_file: DxfFileBase
    ) -> DxfFile:
        project = await Project.by_id(session, dxf_file.project_id)
        file = DxfFile.parse_obj(dxf_file)
        session.add(file)

        project.dxf_file_id = file.id
        session.add(project)

        return file

    async def create_sewer_variants(
        self,
        session: AsyncSession,
        sewer_variants: list[SewerVariantBase],
        project_id: uuid.UUID,
    ) -> list[SewerVariant]:
        old_sewer_variants = await self.get_sewer_variants(session, {project_id})
        for variant in old_sewer_variants:
            await session.delete(variant)

        new_sewer_variants = []
        for sv in sewer_variants:
            new_sewer_variant = SewerVariant(
                project_id=project_id,
                **sv.dict(),
            )
            new_sewer_variants.append(new_sewer_variant)
        session.add_all(new_sewer_variants)
        return new_sewer_variants

    async def get_sewer_variants(
        self, session: AsyncSession, project_ids: set[uuid.UUID]
    ) -> list[SewerVariant]:
        stmt = select(Project).where(col(Project.id).in_(set(project_ids)))
        projects = (await session.execute(stmt)).scalars().all()
        projects_ids_from_db = {p.id for p in projects}

        wrong_project_ids = set(project_ids) - set(projects_ids_from_db)
        if len(wrong_project_ids) > 0:
            raise NoResultFound(f"Projects with ids {wrong_project_ids} were not found")

        stmt = select(SewerVariant).where(col(SewerVariant.project_id).in_(project_ids))
        sewer_variants: list[SewerVariant] = (
            (await session.execute(stmt)).scalars().all()
        )
        return sewer_variants

    async def update_sewer_variant_excel_source_url(
        self, session: AsyncSession, sewer_variant_id: uuid.UUID, new_source_url: str
    ) -> SewerVariant:
        variant = await SewerVariant.by_id(session, sewer_variant_id)
        variant.excel_source_url = new_source_url
        session.add(variant)
        return variant

    async def update_project_status(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
        new_status: ProjectStatusOption,
    ) -> Project:
        project = await Project.by_id(session, project_id)
        project.status = new_status
        session.add(project)
        return project

    # async def get_latest_dxf_file(
    #     self, session: AsyncSession, project_id: uuid.UUID
    # ) -> DxfFile:
    #     await Project.by_id(session, project_id)
    #
    #     stmt = (
    #         select(DxfFile)
    #         .where(DxfFile.project_id == project_id)
    #         .order_by(desc(DxfFile.created_at))
    #         .limit(1)
    #     )
    #     files = (await session.execute(stmt)).scalars().all()
    #
    #     if len(files) == 0:
    #         raise NoResultFound("No DXF files found for this project")
    #
    #     return files[0]

    async def get_dxf_file(self, session: AsyncSession, file_id):
        return await DxfFile.by_id(session, file_id)
