import settings
from fastapi import APIRouter, Depends
from src.db.main_db_manager import MainDbManager
from src.db.projects.models import Fitting, Project

from src.server.auth import Auth
from src.server.common import METHOD
from src.server.projects.endpoints import ProjectsEndpoints
from src.server.projects.models import (
    ProjectExtendedWithNames,
    FittingGroupRead,
    DxfFileWithDevices,
    ProjectWithResults,
)


class ProjectsRouter:
    def __init__(
        self,
        main_db_manager: MainDbManager,
    ):
        self._projects_endpoints = ProjectsEndpoints(main_db_manager)

        self.router = APIRouter(
            prefix=f"{settings.API_PREFIX}/projects",
            tags=["projects"],
        )

        self.router.add_api_route(
            path="/fittings",
            endpoint=self._projects_endpoints.create_fittings,
            response_model=list[Fitting],
            methods=[METHOD.POST],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/fittings-all",
            endpoint=self._projects_endpoints.get_all_fittings,
            response_model=list[FittingGroupRead],
            methods=[METHOD.GET],  # TODO: make GET
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/project",
            endpoint=self._projects_endpoints.create_project,  # TODO: add fittings to the input
            response_model=Project,
            methods=[METHOD.POST],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/project",
            endpoint=self._projects_endpoints.get_project,
            response_model=ProjectExtendedWithNames,
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/projects-all",
            endpoint=self._projects_endpoints.get_all_projects,
            response_model=list[ProjectExtendedWithNames],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/dxf-upload",
            endpoint=self._projects_endpoints.upload_dxf,
            response_model=DxfFileWithDevices,
            methods=[METHOD.POST],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/result",
            endpoint=self._projects_endpoints.build_pipes,
            response_model=ProjectWithResults,
            methods=[METHOD.POST],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        #
        # self.router.add_api_route(
        #     path="/excel-download",
        #     endpoint=self._projects_endpoints.download_excel,
        #     response_model=,
        #     methods=[METHOD.GET],
        #     dependencies=[Depends(Auth(main_db_manager))],
        # )
        #
