from datetime import datetime
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.exc import NoResultFound

from src.db.exceptions import ResourceAlreadyExists
from src.db.main_db_manager import MainDbManager
from src.db.users.models import (
    User,
    UserBase,
    TokenKindOption,
)
from src.server.auth_utils import (
    oauth2_scheme,
    get_user_id_from_token,
    create_user_token,
)
from src.server.common import exc_to_str, HTTPExceptionDetail
from src.server.users.models import (
    TokenWithExpiryData,
    UserCreate,
    UserLogin,
)


class UsersEndpoints:
    def __init__(
        self,
        main_db_manager: MainDbManager,
    ) -> None:
        self._main_db_manager = main_db_manager

    async def create_user(self, user_create: UserCreate) -> User:
        async with self._main_db_manager.users.make_autobegin_session() as session:
            try:
                user = UserBase(name=user_create.name, email=user_create.email)
                new_user = await self._main_db_manager.users.create_user(session, user)
            except ResourceAlreadyExists as e:
                # raise HTTPException(detail=exc_to_str(e), status_code=409)
                error = f"Пользователь с электронной почтой {user.email} уже существует"
                raise HTTPException(
                    detail=[
                        HTTPExceptionDetail(
                            error=error, error_meta={"field": "username"}
                        ).dict()
                    ],
                    status_code=409,
                )
                # return UnifiedResponse(error=exc_to_str(e), status_code=409)

            try:
                await self._main_db_manager.users.create_user_password(
                    session, new_user.id, user_create.password
                )

                return new_user

            except NoResultFound as e:
                raise HTTPException(detail=exc_to_str(e), status_code=404)
                # return UnifiedResponse(error=exc_to_str(e), status_code=404)

    # async def create_project(self, project: ProjectCreate) -> UnifiedResponse[Project]:
    #     proj = ProjectBase.parse_obj(project)
    #     user_id = project.user_id
    #
    #     try:
    #         async with self._main_db_manager.users.make_autobegin_session() as session:
    #             new_project = await self._main_db_manager.users.create_project(
    #                 session, proj, user_id
    #             )
    #     except NoResultFound as e:
    #         # raise HTTPException(status_code=404, detail=e.args)
    #         return UnifiedResponse(error=exc_to_str(e), status_code=404)
    #
    #     # Also need to create a new S3 bucket here
    #
    #     return UnifiedResponse(data=new_project)

    # async def create_user_role(
    #     self, user_role: UserRoleBase
    # ) -> UnifiedResponse[UserRole]:
    #     async with self._main_db_manager.users.make_autobegin_session() as session:
    #         try:
    #             new_user_role = await self._main_db_manager.users.create_user_role(
    #                 session, user_role
    #             )
    #             return UnifiedResponse(data=new_user_role)
    #         except ResourceAlreadyExists as e:
    #             # raise HTTPException(status_code=409, detail=e.args)
    #             return UnifiedResponse(error=exc_to_str(e), status_code=409)
    #         except NoResultFound as e:
    #             # raise HTTPException(status_code=404, detail=e.args)
    #             return UnifiedResponse(error=exc_to_str(e), status_code=404)

    # async def get_user(
    #     self, user_id: Optional[uuid.UUID] = None, email: Optional[str] = None
    # ) -> UnifiedResponse[User]:
    #     async with self._main_db_manager.users.make_autobegin_session() as session:
    #         try:
    #             user = await self._main_db_manager.users.get_user(
    #                 session, user_id=user_id, email=email
    #             )
    #             return UnifiedResponse(data=user)
    #         except (NoResultFound, AssertionError) as e:
    #             # raise HTTPException(status_code=404, detail=e.args)
    #             return UnifiedResponse(error=exc_to_str(e), status_code=404)

    # async def get_user_roles(
    #     self,
    #     user_id: Optional[uuid.UUID] = None,
    #     project_id: Optional[uuid.UUID] = None,
    #     role_type: Optional[RoleTypeOption] = None,
    # ) -> UnifiedResponse[list[UserRoleWithProjectRead]]:
    #     async with self._main_db_manager.users.make_autobegin_session() as session:
    #         try:
    #             user_roles = await self._main_db_manager.users.get_user_roles(
    #                 session, user_id=user_id, project_id=project_id, role_type=role_type
    #             )
    #             resp = [UserRoleWithProjectRead.parse_obj(ur) for ur in user_roles]
    #             return UnifiedResponse(data=resp)
    #         except (NoResultFound, AssertionError) as e:
    #             # raise HTTPException(status_code=404, detail=e.args)
    #             return UnifiedResponse(error=exc_to_str(e), status_code=404)

    async def login_for_access_token(self, form_data: UserLogin) -> TokenWithExpiryData:
        # user = authenticate_user(fake_users_db, form_data.username, form_data.password)
        async with self._main_db_manager.users.make_autobegin_session() as session:
            try:
                user = await self._main_db_manager.users.authenticate_user(
                    session, form_data.username, form_data.password
                )
            except NoResultFound as e:
                error = f"Пользователь с электронной почтой {form_data.username} не зарегистрирован"
                raise HTTPException(
                    detail=[
                        HTTPExceptionDetail(
                            error=error, error_meta={"field": "username"}
                        ).dict()
                    ],
                    status_code=404,
                )
                # raise HTTPException(status_code=404, detail=exc_to_str(e))
                # return UnifiedResponse(error=exc_to_str(e), status_code=404)

        if not user:
            error = f"Неверный пароль"
            raise HTTPException(
                detail=[
                    HTTPExceptionDetail(
                        error=error, error_meta={"field": "password"}
                    ).dict()
                ],
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )
            # raise HTTPException(
            #     status_code=401,
            #     detail={"password": "Неверный пароль"},
            #     headers={"WWW-Authenticate": "Bearer"},
            # )
            # return UnifiedResponse(
            #     error="Incorrect username or password", status_code=401
            # )

        user_token_base = create_user_token(user)
        async with self._main_db_manager.users.make_autobegin_session() as session:
            try:
                user_token = await self._main_db_manager.users.create_user_token(
                    session, user_token_base
                )
            except NoResultFound as e:
                raise HTTPException(status_code=404, detail=exc_to_str(e))
                # return UnifiedResponse(error=exc_to_str(e), status_code=500)

        # return UnifiedResponse(data=user_token)
        # return {"access_token": access_token, "token_type": "bearer"}
        token = TokenWithExpiryData(
            access_token=user_token.access_token,
            refresh_token=user_token.refresh_token,
            token_type=user_token.token_type,
            access_expires_at=(user_token.access_expires_at - datetime.now()).seconds,
            refresh_expires_at=(user_token.refresh_expires_at - datetime.now()).seconds,
        )
        # return UnifiedResponse(data=token)
        return token

    async def swagger_login_for_access_token(
        self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ) -> TokenWithExpiryData:
        user_login = UserLogin(username=form_data.username, password=form_data.password)
        return await self.login_for_access_token(user_login)

    async def get_current_user(
        self, token: Annotated[str, Depends(oauth2_scheme)]
    ) -> User:
        async with self._main_db_manager.users.make_autobegin_session() as session:
            try:
                user_id = get_user_id_from_token(token)
                user = await self._main_db_manager.users.get_user(
                    session, user_id=user_id
                )
            except JWTError as e:
                error = f"Ошибка валидации данных"
                raise HTTPException(
                    detail=[HTTPExceptionDetail(error=error).dict()], status_code=404
                )
                # raise HTTPException(detail=exc_to_str(e), status_code=401)
                # return UnifiedResponse(error=exc_to_str(e), status_code=401)
        return user

    async def refresh_token(self, refresh_token: str) -> TokenWithExpiryData:
        async with self._main_db_manager.users.make_autobegin_session() as session:
            is_valid = await self._main_db_manager.users.is_token_valid(
                session, refresh_token, token_kind=TokenKindOption.refresh
            )
            if not is_valid:
                # return UnifiedResponse(
                #     error="Refresh token has expired", status_code=401
                # )
                raise HTTPException(detail="Рефреш-токен устарел", status_code=401)

            user_id = get_user_id_from_token(refresh_token)

            user = await self._main_db_manager.users.get_user(session, user_id=user_id)

            user_token_base = create_user_token(user)

            new_user_token = await self._main_db_manager.users.create_user_token(
                session, user_token_base
            )

            await self._main_db_manager.users.invalidate_previous_token(
                session, refresh_token
            )

        token = TokenWithExpiryData(
            access_token=new_user_token.access_token,
            refresh_token=new_user_token.refresh_token,
            token_type=new_user_token.token_type,
            access_expires_at=(
                new_user_token.access_expires_at - datetime.now()
            ).seconds,
            refresh_expires_at=(
                new_user_token.refresh_expires_at - datetime.now()
            ).seconds,
        )
        return token
