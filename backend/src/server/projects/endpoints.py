import base64
import os
import uuid
from _decimal import Decimal
from collections import defaultdict
from typing import Annotated, Optional

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
    ProjectStatusOption,
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
    ProjectsDelete,
    ProjectSewerVariant,
    FittingStat,
    ProjectResultFittingsStat,
    ProjectsStats,
    DeviceStats,
)
from src.trace_builder.projections import clear_sutff_duplicate
from src.trace_builder.run import run_algo
from src.trace_builder.utils import convert_dxf2img


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
                status_code=400,
                detail="Автор и Исполнитель не может быть одним человеком",
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

    async def get_project(self, project_id: uuid.UUID) -> ProjectWithResults:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                project = await self._main_db_manager.projects.get_project(
                    session, project_id
                )
            except NoResultFound as e:
                raise HTTPException(status_code=404, detail=exc_to_str(e))

        if project.status == ProjectStatusOption.ready:
            project_with_results = await self._get_project_with_results(project_id)
            return project_with_results

        else:  # TODO: Most probably this case can be covered with the first one, cause if no results found,
            # the list will be empty (So maybe I'll have to put None there by hands after the _get_project_with... run
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
                except NoResultFound as e:
                    raise HTTPException(status_code=404, detail=exc_to_str(e))
                proj = ProjectWithResults(
                    author_name=user_by_id[project.author_id].name,
                    worker_name=user_by_id[project.worker_id].name,
                    **project.dict(),
                )
                return proj

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

    async def delete_projects(self, projects_delete: ProjectsDelete) -> list[Project]:
        try:
            async with self._main_db_manager.projects.make_autobegin_session() as session:
                projects = await self._main_db_manager.projects.delete_projects(
                    session, projects_delete.project_ids
                )
        except NoResultFound as e:
            raise HTTPException(status_code=404, detail=exc_to_str(e))
        return projects

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
        stuffs = clear_sutff_duplicate(stuffs)

        dxf_file = DxfFile(project_id=project_id, source_url=file_name)

        dxf_file_screenshot_path = str(file_path)[:-3] + "png"
        convert_dxf2img(doc, dxf_file_screenshot_path, img_res=200)
        with open(dxf_file_screenshot_path, "rb") as img:
            dxf_file_screenshot = base64.b64encode(img.read()).decode("utf-8")

        try:
            async with self._main_db_manager.projects.make_autobegin_session() as session:
                dxf_file_created = await self._main_db_manager.projects.create_dxf_file(
                    session, dxf_file
                )
                # Project should get status "in_progress" when pipe building is launched. Currently an algo works fast
                # so I immediately switch status to "ready" after pipe building. Status "in_progress" should be used
                # if we decide to use algo that works significantly longer.

                # await self._main_db_manager.projects.update_project_status(
                #     session, project_id, ProjectStatusOption.in_progress
                # )
        except NoResultFound as e:
            raise HTTPException(status_code=404, detail=exc_to_str(e))

        devices = []
        for stuff_name, coords in stuffs.items():
            device_type = self._device_type_by_name(stuff_name)
            if device_type is None:  # Unknown device
                continue
            device = Device(
                dxf_file_id=dxf_file_created.id,
                name=stuff_name,
                type=device_type,
                type_human=device_type_to_name[device_type],
                coord_x=round(coords[0]),
                coord_y=round(coords[1]),
            )
            devices.append(device)

        try:
            async with self._main_db_manager.projects.make_autobegin_session() as session:
                devices_created = await self._main_db_manager.projects.create_devices(
                    session, devices
                )
        except NoResultFound as e:
            raise HTTPException(status_code=404, detail=exc_to_str(e))

        res = DxfFileWithDevices(
            id=dxf_file_created.id,
            project_id=project_id,
            devices=devices_created,
            image=dxf_file_screenshot,
            type="Кабина",
        )
        return res

    def _device_type_by_name(self, device_name: str) -> Optional[DeviceTypeOption]:
        if "унитаз" in device_name.lower():
            device_type = DeviceTypeOption.toilet
        elif "раковина" in device_name.lower():
            device_type = DeviceTypeOption.sink
        elif "машина" in device_name.lower():
            device_type = DeviceTypeOption.washing_machine
        elif "ванна" in device_name.lower():
            device_type = DeviceTypeOption.bath
        elif "кран" in device_name.lower():
            device_type = DeviceTypeOption.faucet
        elif "мойка" in device_name.lower():
            device_type = DeviceTypeOption.kitchen_sink
        else:
            print(f"Unknown device {device_name}")
            device_type = None
        return device_type

    async def _get_project_with_results(
        self, project_id: uuid.UUID
    ) -> ProjectWithResults:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            variants = await self._main_db_manager.projects.get_sewer_variants(
                session, {project_id}
            )

        stats_table: defaultdict[str, list[FittingStat]] = defaultdict(list)
        connection_points_table: defaultdict[str, list[ConnectionPoint]] = defaultdict(
            list
        )
        graph_table: defaultdict[str, list[GraphVertex]] = defaultdict(list)
        imgs: dict[str, str] = dict()
        for variant in variants:
            stats_df = pd.read_excel(variant.excel_source_url, sheet_name="Материалы")
            connection_points_df = pd.read_excel(
                variant.excel_source_url, sheet_name="Точки подключения"
            )
            graph_df = pd.read_excel(
                variant.excel_source_url, sheet_name="Граф подключения фитингов"
            )

            for idx, row in stats_df.iterrows():
                stat = FittingStat(
                    name=row["Наименование"],
                    material_id=row["ИД материала"],
                    n_items=row["Кол-во"],
                )
                stats_table[variant.variant_num].append(stat)

            for idx, row in connection_points_df.iterrows():
                connection_point = ConnectionPoint(
                    id=uuid.uuid4(),
                    type=row["Тип"],
                    diameter=row["Диаметр"],
                    coord_x=row["X"],
                    coord_y=row["Y"],
                    coord_z=row["Z"],
                )
                connection_points_table[variant.variant_num].append(connection_point)

            for idx, row in graph_df.iterrows():
                graph = GraphVertex(
                    id=uuid.uuid4(),
                    graph=row["Граф"],
                    material=row["Материал"],
                    # probability=0.9,
                )
                graph_table[variant.variant_num].append(graph)

            with open(variant.png_source_url, "rb") as img:
                img_str = base64.b64encode(img.read()).decode("utf-8")
                imgs[variant.variant_num] = img_str

        async with self._main_db_manager.users.make_autobegin_session() as session:
            users = await self._main_db_manager.users.get_all_users(session)
        user_by_id: dict[uuid.UUID, User] = dict()
        for user in users:
            user_by_id[user.id] = user

        async with self._main_db_manager.projects.make_autobegin_session() as session:
            project = await self._main_db_manager.projects.get_project(
                session, project_id
            )
            proj = ProjectExtendedWithNames(
                author_name=user_by_id[project.author_id].name,
                worker_name=user_by_id[project.worker_id].name,
                **project.dict(),
            )

        project_with_results = ProjectWithResults(
            id=proj.id,
            author_name=proj.author_name,
            worker_name=proj.worker_name,
            name=proj.name,
            description=proj.description,
            status=proj.status,
            type=proj.type,
            bathroom_type=proj.bathroom_type,
            is_deleted=proj.is_deleted,
            dxf_file_id=proj.dxf_file_id,
            created_at=proj.created_at,
            results=[
                ProjectSewerVariant(
                    variant_num=variant.variant_num,
                    n_fittings=variant.n_fittings,
                    sewer_length=variant.sewer_length,
                    result=ProjectResult(
                        fittings_stat=ProjectResultFittingsStat(
                            tab_name="Используемые фитинги",
                            table=stats_table[variant.variant_num],
                            image=imgs[variant.variant_num],
                        ),
                        connection_points=ProjectResultConnectionPoints(
                            tab_name="Точки подключения",
                            table=connection_points_table[variant.variant_num],
                            image=imgs[variant.variant_num],
                        ),
                        graph=ProjectResultGraph(
                            tab_name="Граф подключения",
                            table=graph_table[variant.variant_num],
                            image=imgs[variant.variant_num],
                        ),
                    ),
                )
                for variant in variants
            ],
        )
        return project_with_results

    async def build_pipes(
        self, devices_configs: DevicesWithHeights
    ) -> ProjectWithResults:
        devices = devices_configs.devices
        project_id = devices_configs.project_id
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
        stuffs = clear_sutff_duplicate(stuffs)

        names_to_coord_z = dict()
        for stuff_name, coords in stuffs.items():
            device_type = self._device_type_by_name(stuff_name)
            if device_type is not None:
                names_to_coord_z[stuff_name] = types_to_coord_z[device_type]

        # csv_path, png_path, stl_path = run_algo(
        sewer_variants = run_algo(
            file_path,
            names_to_coord_z,
            settings.MEDIA_DIR / "builder_outputs",
            f"_{devices_configs.dxf_file_id}",
        )

        devices_z_coords = {d.id: d.coord_z for d in devices}

        async with self._main_db_manager.projects.make_autobegin_session() as session:
            variants = await self._main_db_manager.projects.create_sewer_variants(
                session, sewer_variants, project_id
            )
            devices = await self._main_db_manager.projects.update_devices_z_coord(
                session, devices_z_coords
            )
            await self._main_db_manager.projects.update_project_status(
                session, project_id, ProjectStatusOption.ready
            )

        await self._create_excels_for_variants(project_id)

        project_with_results = await self._get_project_with_results(project_id)

        return project_with_results

    async def export_files(
        self,
        project_id: uuid.UUID,
        variant_num: int = 1,
        file_type: ExportFileType = ExportFileType.excel,
    ):
        # filename, file_path = await self._get_filename(project_id, variant_num, file_type)
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                sewer_variants = (
                    await self._main_db_manager.projects.get_sewer_variants(
                        session, {project_id}
                    )
                )
            except NoResultFound as e:
                raise HTTPException(status_code=404, detail=exc_to_str(e))

        sewer_variant = None
        for sw in sewer_variants:
            if sw.variant_num == variant_num:
                sewer_variant = sw

        if file_type == ExportFileType.excel:
            filename = sewer_variant.excel_source_url
            media_type = "application/vnd.ms-excel"
        elif file_type == ExportFileType.stl:
            filename = sewer_variant.stl_source_url
            media_type = "application/wavefront-stl"
        elif file_type == ExportFileType.png:
            filename = sewer_variant.png_source_url
            media_type = "image/png"
        else:
            raise ValueError(f"Unsupported file type")
        headers = {
            "Content-Disposition": f"attachment; filename={filename.split('/')[-1]}"
        }
        return FileResponse(
            filename,
            media_type=media_type,
            headers=headers,
            status_code=200,
        )

    async def get_projects_stats(self) -> ProjectsStats:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            projects = await self._main_db_manager.projects.get_all_projects(session)
            projects_ids = {p.id for p in projects}
            variants = await self._main_db_manager.projects.get_sewer_variants(
                session, projects_ids
            )
            devices = await self._main_db_manager.projects.get_devices(
                session, projects_ids
            )

        if len(variants) == 0:
            projects_stats = ProjectsStats(
                avg_n_fittings=0,
                avg_sewer_length=0,
                devices=[],
            )
        else:
            avg_n_fittings = Decimal(
                sum([v.n_fittings for v in variants]) / len(variants)
            )
            avg_sewer_length = Decimal(
                sum([v.sewer_length for v in variants]) / len(variants)
            )

            devices_stats: defaultdict[str, int] = defaultdict(int)
            for device in devices:
                devices_stats[device.type_human] += 1

            projects_stats = ProjectsStats(
                avg_n_fittings=avg_n_fittings,
                avg_sewer_length=avg_sewer_length,
                devices=[
                    DeviceStats(type_human=type_human, n_occur=n_occur)
                    for type_human, n_occur in devices_stats.items()
                ],
            )
        return projects_stats

    async def _create_excels_for_variants(self, project_id: uuid.UUID) -> None:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            devices = await self._main_db_manager.projects.get_devices(
                session, {project_id}
            )
            variants = await self._main_db_manager.projects.get_sewer_variants(
                session, {project_id}
            )
            fittings = await self._main_db_manager.projects.get_all_fittings(session)

        fitting_material_to_object: dict[str, Fitting] = dict()
        for fitting in fittings:
            if fitting.material_id is not None:
                fitting_material_to_object[fitting.material_id] = fitting

        graph_dfs: dict[int, pd.DataFrame] = dict()
        imgs: dict[int, str] = dict()
        fittings_stat: defaultdict[int, list[FittingStat]] = defaultdict(list)
        for idx, variant in enumerate(variants):
            graph_dfs[variant.variant_num] = pd.read_csv(variant.excel_source_url)

            with open(variant.png_source_url, "rb") as img:
                img_str = base64.b64encode(img.read()).decode("utf-8")
                imgs[variant.variant_num] = img_str

            material_id_to_count: defaultdict[str, int] = defaultdict(int)
            for _, row in graph_dfs[variant.variant_num].iterrows():
                material_id_to_count[str(row["Материал"])] += 1

            for material_id, n_items in material_id_to_count.items():
                if material_id in fitting_material_to_object:
                    # TODO: It should be True allways, but on 08.06.23 we don't have
                    #  straight pipes in "fittings" table in the DB
                    stat = FittingStat(
                        name=fitting_material_to_object[str(material_id)].name,
                        material_id=str(material_id),
                        n_items=n_items,
                        total_length=None,
                    )
                    fittings_stat[variant.variant_num].append(stat)

        for variant in variants:
            stat_dict = dict()
            stat_dict["Наименование"] = [
                fs.name for fs in fittings_stat[variant.variant_num]
            ]
            stat_dict["ИД материала"] = [
                fs.material_id for fs in fittings_stat[variant.variant_num]
            ]
            stat_dict["Кол-во"] = [
                fs.n_items for fs in fittings_stat[variant.variant_num]
            ]
            # stat['Наименование'] = [fs.name for fs in fittings_stat[variant.variant_num]]

            connection_points_dict = dict()
            connection_points_dict["Тип"] = [device.type_human for device in devices]
            connection_points_dict["Диаметр"] = [
                110 if device.type == DeviceTypeOption.toilet else 50
                for device in devices
            ]
            connection_points_dict["X"] = [device.coord_x for device in devices]
            connection_points_dict["Y"] = [device.coord_y for device in devices]
            connection_points_dict["Z"] = [device.coord_z for device in devices]

            graph_dict = dict()
            graph_dict["Граф"] = [
                row["Граф"] for idx, row in graph_dfs[variant.variant_num].iterrows()
            ]
            graph_dict["Материал"] = [
                row["Материал"]
                for idx, row in graph_dfs[variant.variant_num].iterrows()
            ]

            file_path = variant.stl_source_url[:-3] + "xlsx"
            with pd.ExcelWriter(file_path) as writer:
                pd.DataFrame(stat_dict).to_excel(
                    writer, sheet_name="Материалы", index=False
                )
                pd.DataFrame(connection_points_dict).to_excel(
                    writer, sheet_name="Точки подключения", index=False
                )
                pd.DataFrame(graph_dict).to_excel(
                    writer, sheet_name="Граф подключения фитингов", index=False
                )

            async with self._main_db_manager.projects.make_autobegin_session() as session:
                await self._main_db_manager.projects.update_sewer_variant_excel_source_url(
                    session, variant.id, file_path
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
