import base64
import os
import uuid
from collections import defaultdict
from os.path import isfile, join
from typing import Annotated

import aiofiles
import ezdxf
import pandas as pd
from fastapi import HTTPException, Depends, UploadFile
from sqlalchemy.exc import NoResultFound
from starlette.responses import FileResponse

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
    DevicesWithHeights,
    ProjectWithResults,
    ProjectResult,
    ProjectResultConnectionPoints,
    ConnectionPoint,
    ProjectResultGraph,
    GraphVertex,
    ExportFileType,
)
from src.trace_builder.run import run_algo


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

        dxf_file = DxfFile(project_id=project_id, source_url=file_name)

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
                coord_x=round(coords[0]),
                coord_y=round(coords[1]),
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

    async def build_pipes(
        self, devices_configs: DevicesWithHeights
    ) -> ProjectWithResults:
        """
        Appropriate DXF file can be found as one with largest created_at for this project_id
        :param devices_configs:
        :return:
        """
        devices = devices_configs.devices
        # Assuming that there can no be two devices with the same type
        types_to_coord_z = dict()
        for device in devices:
            types_to_coord_z[device.type] = device.coord_z

        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                # dxf_file = await self._main_db_manager.projects.get_latest_dxf_file(
                #     session, project_id=devices_configs.project_id
                # )
                dxf_file = await self._main_db_manager.projects.get_dxf_file(
                    session, file_id=devices_configs.dxf_file_id
                )
            except NoResultFound as e:
                raise HTTPException(status_code=404, detail=exc_to_str(e))

        file_path = settings.MEDIA_DIR / "dxf_files" / dxf_file.source_url
        # file_path = settings.BASE_DIR.parent / 'media' / 'dxf_files' / dxf_file.source_url
        doc = ezdxf.readfile(file_path)
        modelspace = doc.modelspace()
        stuffs = entities_with_coordinates(modelspace)

        names_to_coord_z = dict()
        for stuff_name, coords in stuffs.items():
            if "унитаз" in stuff_name.lower():
                names_to_coord_z[stuff_name] = types_to_coord_z[DeviceTypeOption.toilet]
            elif "раковина" in stuff_name.lower():
                names_to_coord_z[stuff_name] = types_to_coord_z[DeviceTypeOption.sink]
            elif "машина" in stuff_name.lower():
                names_to_coord_z[stuff_name] = types_to_coord_z[
                    DeviceTypeOption.washing_machine
                ]
            elif "ванна" in stuff_name.lower():
                names_to_coord_z[stuff_name] = types_to_coord_z[DeviceTypeOption.bath]
            elif "кран" in stuff_name.lower():
                names_to_coord_z[stuff_name] = types_to_coord_z[DeviceTypeOption.faucet]
            elif "мойка" in stuff_name.lower():
                names_to_coord_z[stuff_name] = types_to_coord_z[
                    DeviceTypeOption.kitchen_sink
                ]

        csv_path, png_path, stl_path = run_algo(
            file_path,
            names_to_coord_z,
            settings.MEDIA_DIR / "builder_outputs",
            f"_{devices_configs.dxf_file_id}",
        )

        df = pd.read_csv(csv_path)

        with open(png_path, "rb") as img:
            img_str = base64.b64encode(img.read()).decode("utf-8")

        async with self._main_db_manager.users.make_autobegin_session() as session:
            users = await self._main_db_manager.users.get_all_users(session)
        user_by_id: dict[uuid.UUID, User] = dict()
        for user in users:
            user_by_id[user.id] = user

        async with self._main_db_manager.projects.make_autobegin_session() as session:
            project = await self._main_db_manager.projects.get_project(
                session, devices_configs.project_id
            )
            proj = ProjectExtendedWithNames(
                author_name=user_by_id[project.author_id].name,
                worker_name=user_by_id[project.worker_id].name,
                **project.dict(),
            )

        p = ProjectWithResults(
            id=proj.id,
            author_name=proj.author_name,
            worker_name=proj.worker_name,
            name=proj.name,
            description=proj.description,
            status=proj.status,
            type=proj.type,
            bathroom_type=proj.bathroom_type,
            is_deleted=proj.is_deleted,
            result=ProjectResult(
                connection_points=ProjectResultConnectionPoints(
                    tab_name="Точки подключения",
                    table=[
                        ConnectionPoint(
                            id=uuid.uuid4(),
                            order="direct",
                            type=device.type,
                            diameter=1,
                            coord_x=device.coord_x,
                            coord_y=device.coord_y,
                            coord_z=device.coord_z,
                        )
                        for device in devices
                    ],
                    image=img_str,
                ),
                graph=ProjectResultGraph(
                    tab_name="Граф подключения",
                    table=[
                        GraphVertex(
                            id=uuid.uuid4(),
                            graph=row["Граф"],
                            material=row["Материал"],
                            probability=0.9,
                        )
                        for id, row in df.iterrows()
                    ],
                    image=img_str,
                ),
            ),
        )

        return p

    async def export_files(
        self,
        project_id: uuid.UUID,
        variant_num: int = 1,
        file_type: ExportFileType = ExportFileType.csv,
    ):
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            dxf_file = await self._main_db_manager.projects.get_latest_dxf_file(
                session, project_id=project_id
            )

        files_dir = settings.MEDIA_DIR / "builder_outputs"
        filenames_all = [f for f in os.listdir(files_dir) if isfile(join(files_dir, f))]
        if file_type == ExportFileType.csv:
            filenames = [f for f in filenames_all if f.endswith(f"{dxf_file.id}.csv")]
            media_type = "text/csv"
        elif file_type == ExportFileType.stl:
            filenames = [f for f in filenames_all if f.endswith(f"{dxf_file.id}.stl")]
            media_type = "application/wavefront-stl"
        needed_filename = filenames[0]
        headers = {"Content-Disposition": f"attachment; filename={needed_filename}"}
        return FileResponse(
            files_dir / needed_filename,
            media_type=media_type,
            headers=headers,
            status_code=200,
        )

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
