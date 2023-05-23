import settings
from fastapi import APIRouter
from src.db.main_db_manager import MainDbManager
from src.db.users.models import User
from src.server.common import METHOD
from src.server.users.endpoints import UsersEndpoints
from src.server.users.models import TokenWithExpiryData


class UsersRouter:
    def __init__(
        self,
        main_db_manager: MainDbManager,
    ):
        self._users_endpoints = UsersEndpoints(main_db_manager)

        self.router = APIRouter(
            prefix=f"{settings.APP_PREFIX}/users",
            tags=["users"],
        )

        self.router.add_api_route(
            path="/user",
            endpoint=self._users_endpoints.create_user,
            response_model=User,
            methods=[METHOD.POST],
        )

        # self.router.add_api_route(
        #     path="/user-role",
        #     endpoint=self._users_endpoints.create_user_role,
        #     response_model=UnifiedResponse[UserRole],
        #     methods=[METHOD.POST],
        #     dependencies=[Depends(Auth(main_db_manager))],
        # )

        # self.router.add_api_route(
        #     path="/project",
        #     endpoint=self._users_endpoints.create_project,
        #     response_model=UnifiedResponse[Project],
        #     methods=[METHOD.POST],
        #     dependencies=[Depends(Auth(main_db_manager))],
        # )

        # self.router.add_api_route(
        #     path="/user",
        #     endpoint=self._users_endpoints.get_user,
        #     response_model=UnifiedResponse[User],
        #     methods=[METHOD.GET],
        #     description="Get user by user_id/email",
        #     responses={404: {"description": "User not found"}},
        # )

        # self.router.add_api_route(
        #     path="/user-role",
        #     endpoint=self._users_endpoints.get_user_roles,
        #     response_model=UnifiedResponse[list[UserRoleWithProjectRead]],
        #     methods=[METHOD.GET],
        #     description="Get roles user_id or/and by project_id."
        #     "Optionally results can be filtered by role_type "
        #     "(E.g. getting all verificators for the particular project)",
        #     responses={
        #         404: {
        #             "description": "user_id/project_id is not specified or "
        #             "user/project by requested parameters was not found"
        #         }
        #     },
        #     dependencies=[Depends(Auth(main_db_manager))],
        # )

        self.router.add_api_route(
            path="/token",
            endpoint=self._users_endpoints.login_for_access_token,
            response_model=TokenWithExpiryData,
            methods=[METHOD.POST],
        )

        # self.router.add_api_route(
        #     path="/swagger-token",
        #     endpoint=self._users_endpoints.swagger_login_for_access_token,
        #     response_model=Token,
        #     methods=[METHOD.POST],
        # )

        self.router.add_api_route(
            path="/token-refresh",
            endpoint=self._users_endpoints.refresh_token,
            response_model=TokenWithExpiryData,
            methods=[METHOD.POST],
        )

        self.router.add_api_route(
            path="/me",
            endpoint=self._users_endpoints.get_current_user,
            response_model=User,
            methods=[METHOD.GET],
        )
