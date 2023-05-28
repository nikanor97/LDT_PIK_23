import os
import uuid
from collections import defaultdict
from typing import Annotated

import aiofiles
import ezdxf
from fastapi import HTTPException, Depends, UploadFile
from sqlalchemy.exc import NoResultFound

import settings
from src.architecture_utils.dxf import entities_with_coordinates
from src.server.constants import FittingCreate
from src.db.main_db_manager import MainDbManager
from src.db.projects.models import (
    Fitting,
    ProjectBase,
    Project,
    RoleTypeOption,
    UserRoleBase,
    DxfFile,
    Device,
    device_type_to_name,
    DeviceTypeOption,
)
from src.db.users.models import User
from src.server.auth_utils import oauth2_scheme, get_user_id_from_token
from src.server.common import exc_to_str

from src.server.projects.models import (
    ProjectCreate,
    ProjectExtendedWithNames,
    FittingGroupRead,
    FittingRead,
    DxfFileWithDevices,
)


class ProjectsEndpoints:
    def __init__(
        self,
        main_db_manager: MainDbManager,
    ) -> None:
        self._main_db_manager = main_db_manager

    async def create_fittings(self, fittings: list[FittingCreate]) -> list[Fitting]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            # try:
            result = await self._main_db_manager.projects.create_fittins(
                session, fittings
            )
            # except NoResultFound as e:
            #     return UnifiedResponse(error=exc_to_str(e), status_code=404)
        return result

    async def get_all_fittings(
        self,
    ) -> list[FittingGroupRead]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            fittings = await self._main_db_manager.projects.get_all_fittings(session)

        groupname_to_fittings: defaultdict[str, list[Fitting]] = defaultdict(list)
        for fitting in fittings:
            groupname_to_fittings[fitting.groupname].append(fitting)

        result = []
        for groupname, fittings_ in groupname_to_fittings.items():
            fit = FittingGroupRead(
                groupname=groupname,
                values=[
                    FittingRead(image=f.image_b64, name=f.name, id=f.id)
                    for f in fittings_
                ],
            )
            result.append(fit)

        return result

    async def create_project(
        self, project: ProjectCreate, token: Annotated[str, Depends(oauth2_scheme)]
    ) -> Project:
        proj = ProjectBase.parse_obj(project)
        user_id = get_user_id_from_token(token)

        if project.worker_id == user_id:
            raise HTTPException(
                status_code=400, detail="Author and Worker can not be the same person"
            )

        if len(project.fittings_ids) == 0:
            raise HTTPException(
                status_code=400, detail="Fittings array can not be empty"
            )

        # Checking whether user with user_id exists
        user = await self._get_user_or_error(user_id)
        if isinstance(user, NoResultFound):
            # return UnifiedResponse(error=exc_to_str(user), status_code=404)
            raise HTTPException(status_code=404, detail=exc_to_str(user))

        # Checking whether users with workers_ids exist in the DB
        async with self._main_db_manager.users.make_autobegin_session() as session:
            try:
                await self._main_db_manager.users.get_users(
                    session, {project.worker_id}
                )
            except NoResultFound as e:
                # return UnifiedResponse(error=exc_to_str(e), status_code=404)
                raise HTTPException(status_code=404, detail=exc_to_str(e))

        async with self._main_db_manager.projects.make_autobegin_session() as session:
            # async with AsyncTransaction(session.connection) as trans:
            try:
                # TODO: implement transactional behaviour here !!!

                new_project = await self._main_db_manager.projects.create_project(
                    session, proj, user_id
                )

                await self._main_db_manager.projects.create_project_fittings(
                    session, new_project.id, project.fittings_ids
                )

                fittings = await self._main_db_manager.projects.get_fittings_by_project(
                    session, new_project.id
                )

                # Checking if any workers with workers_ids are already assigned to the project
                existing_user_roles = (
                    await self._main_db_manager.projects.get_user_roles(
                        session,
                        project_id=new_project.id,
                        role_type=RoleTypeOption.worker,
                    )
                )
                not_assigned_users_ids = {project.worker_id} - set(
                    [eur.user_id for eur in existing_user_roles]
                )
                for u_id in not_assigned_users_ids:
                    ur = UserRoleBase(
                        project_id=new_project.id,
                        user_id=u_id,
                        role_type=RoleTypeOption.worker,
                    )
                    await self._main_db_manager.projects.create_user_role(session, ur)

            except NoResultFound as e:
                # return UnifiedResponse(error=exc_to_str(e), status_code=404)
                raise HTTPException(status_code=404, detail=exc_to_str(e))

        return new_project

    async def get_project(self, project_id: uuid.UUID) -> ProjectExtendedWithNames:
        async with self._main_db_manager.users.make_autobegin_session() as session:
            users = await self._main_db_manager.users.get_all_users(session)
        user_by_id: dict[uuid.UUID, User] = dict()
        for user in users:
            user_by_id[user.id] = user

        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                project = await self._main_db_manager.projects.get_project(
                    session, project_id
                )
                proj = ProjectExtendedWithNames(
                    author_name=user_by_id[project.author_id].name,
                    worker_name=user_by_id[project.worker_id].name,
                    **project.dict(),
                )
                return proj
            except NoResultFound as e:
                # return UnifiedResponse(error=exc_to_str(e), status_code=404)
                raise HTTPException(status_code=404, detail=exc_to_str(e))

    async def get_all_projects(self) -> list[ProjectExtendedWithNames]:
        async with self._main_db_manager.users.make_autobegin_session() as session:
            users = await self._main_db_manager.users.get_all_users(session)
        user_by_id: dict[uuid.UUID, User] = dict()
        for user in users:
            user_by_id[user.id] = user

        async with self._main_db_manager.projects.make_autobegin_session() as session:
            projects = await self._main_db_manager.projects.get_all_projects(session)
            result = []
            for project in projects:
                proj = ProjectExtendedWithNames(
                    author_name=user_by_id[project.author_id].name,
                    worker_name=user_by_id[project.worker_id].name,
                    **project.dict(),
                )
                result.append(proj)

            return result

    async def upload_dxf(
        self, project_id: uuid.UUID, file: UploadFile
    ) -> DxfFileWithDevices:
        try:
            async with self._main_db_manager.projects.make_autobegin_session() as session:
                project = await self._main_db_manager.projects.get_project(
                    session, project_id
                )
        except NoResultFound as e:
            raise HTTPException(status_code=404, detail=exc_to_str(e))

        file_id = uuid.uuid4()
        if file.filename is not None:
            file_name = f'{".".join(file.filename.split(".")[:-1])}_{file_id}.dxf'
        else:
            file_name = f"{file_id}.dxf"
        file_path = settings.MEDIA_DIR / "dxf_files" / file_name
        os.makedirs(settings.MEDIA_DIR / "dxf_files", exist_ok=True)

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(await file.read())

        doc = ezdxf.readfile(file_path)
        modelspace = doc.modelspace()
        stuffs = entities_with_coordinates(modelspace)

        dxf_file = DxfFile(project_id=project_id, source_url=file_path)

        devices = []
        for stuff_name, coords in stuffs.items():
            if "унитаз" in stuff_name.lower():
                device_type = DeviceTypeOption.toilet
            elif "раковина" in stuff_name.lower():
                device_type = DeviceTypeOption.sink
            elif "машина" in stuff_name.lower():
                device_type = DeviceTypeOption.washing_machine
            elif "ванна" in stuff_name.lower():
                device_type = DeviceTypeOption.bath
            elif "кран" in stuff_name.lower():
                device_type = DeviceTypeOption.faucet
            elif "мойка" in stuff_name.lower():
                device_type = DeviceTypeOption.kitchen_sink
            else:
                print(f"Unknown device {stuff_name}")
                continue
            device = Device(
                project_id=project_id,
                name=device_type_to_name[device_type],
                type=device_type,
                coord_x=coords[0],
                coord_y=coords[1],
            )
            devices.append(device)

        try:
            async with self._main_db_manager.projects.make_autobegin_session() as session:
                devices_created = await self._main_db_manager.projects.create_devices(
                    session, devices
                )
                dxf_file_created = await self._main_db_manager.projects.create_dxf_file(
                    session, dxf_file
                )

        except NoResultFound as e:
            raise HTTPException(status_code=404, detail=exc_to_str(e))

        res = DxfFileWithDevices(
            id=dxf_file_created.id,
            project_id=project_id,
            devices=devices_created,
            type="Кабина",
        )
        return res

    async def _get_user_or_error(self, user_id: uuid.UUID) -> User | NoResultFound:
        """
        Method should be used only inside endpoints class.
        :return: User if user with user_id exists else NoResultFound error
        """
        async with self._main_db_manager.users.make_autobegin_session() as session:
            try:
                user = await self._main_db_manager.users.get_user(
                    session, user_id=user_id
                )
                return user
            except (NoResultFound, AssertionError) as e:
                return e
