import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.base_manager import BaseDbManager
from src.db.exceptions import ResourceAlreadyExists
from src.db.users.models import (
    User,
    UserBase,
    UserPassword,
    UserToken,
    UserTokenBase,
    TokenKindOption,
)
from src.server.auth_utils import verify_password, get_password_hash


# TODO: Replace all "create" method with session.add cause otherwise in case
#  of several creations some objects can be created and others will fail (non-transactional behaviour)


class UsersDbManager(BaseDbManager):
    async def create_user(self, session: AsyncSession, user: UserBase) -> User:
        existing_user = (
            await session.execute(select(User).where(User.email == user.email))
        ).scalar_one_or_none()
        if existing_user is None:
            created_user = await User.create(session, user)
            return created_user
        else:
            # raise ResourceAlreadyExists(f"Пользователь с электронной почтой {user.email} уже существует")
            raise ResourceAlreadyExists(f"User with email {user.email} already exists")

    # async def create_project(
    #     self, session: AsyncSession, project: ProjectBase, user_id: uuid.UUID
    # ) -> Project:
    #     # Checking if user with this id exists
    #     await User.by_id(session, user_id)
    #
    #     new_project = Project.parse_obj(project)
    #     session.add(new_project)
    #
    #     new_user_role = UserRole(
    #         user_id=user_id, project_id=new_project.id, role_type=RoleTypeOption.author
    #     )
    #     session.add(new_user_role)
    #
    #     await session.commit()
    #
    #     return new_project

    # async def create_user_role(
    #     self, session: AsyncSession, user_role: UserRoleBase
    # ) -> UserRole:
    #     # Checking if user with this id exists
    #     await User.by_id(session, user_role.user_id)
    #
    #     # Checking if project with this id exists
    #     await Project.by_id(session, user_role.project_id)
    #
    #     existing_user_role = (
    #         await session.execute(
    #             select(UserRole)
    #             .where(UserRole.role_type == user_role.role_type)
    #             .where(UserRole.user_id == user_role.user_id)
    #             .where(UserRole.project_id == user_role.project_id)
    #         )
    #     ).scalar_one_or_none()
    #     if existing_user_role is None:
    #         created_user_role = await UserRole.create(session, user_role)
    #         return created_user_role
    #     else:
    #         raise ResourceAlreadyExists(
    #             f"User role with role_type {user_role.role_type}, "
    #             f"user_id {user_role.user_id} and "
    #             f"project_id {user_role.project_id} already exists"
    #         )

    async def get_user(
        self,
        session: AsyncSession,
        *,
        user_id: Optional[uuid.UUID] = None,
        email: Optional[str] = None,
    ) -> User:
        assert (
            user_id is not None or email is not None
        ), "Либо user_id либо email должен быть не пустым"

        user: Optional[User] = None
        if user_id is not None:
            user = await User.by_id(session, user_id)
        elif email is not None:
            stmt = select(User).where(User.email == email)
            user = (await session.execute(stmt)).scalar_one_or_none()
            if user is None:
                raise NoResultFound(
                    f"Пользователь с электронной почтой {email} не зарегистрирован"
                )

        assert user is not None
        return user

    # async def get_user_roles(
    #     self,
    #     session: AsyncSession,
    #     *,
    #     user_id: Optional[uuid.UUID] = None,
    #     project_id: Optional[uuid.UUID] = None,
    #     role_type: Optional[RoleTypeOption] = None,
    # ) -> list[UserRole]:
    #     assert (
    #         user_id is not None or project_id is not None
    #     ), "Либо user_id либо project_id должен быть не пустым"
    #
    #     stmt = select(UserRole)
    #
    #     if user_id is not None:
    #         # Checking if user with this id exists
    #         await User.by_id(session, user_id)
    #         stmt = stmt.where(UserRole.user_id == user_id)
    #     if project_id is not None:
    #         # Checking if project with this id exists
    #         await Project.by_id(session, project_id)
    #         stmt = stmt.where(UserRole.project_id == project_id)
    #     if role_type is not None:
    #         stmt = stmt.where(UserRole.role_type == role_type)
    #
    #     stmt = stmt.options(selectinload(UserRole.user), selectinload(UserRole.project))
    #
    #     return (await session.execute(stmt)).scalars().all()

    # async def get_project(
    #     self, session: AsyncSession, project_id: uuid.UUID
    # ) -> Project:
    #     return await Project.by_id(session, project_id)

    async def authenticate_user(
        self, session: AsyncSession, username: str, password: str
    ) -> Optional[User]:
        stmt = select(User).where(User.email == username)
        user: Optional[User] = (await session.execute(stmt)).scalar_one_or_none()
        if user is None:
            raise NoResultFound(
                f"Пользователь с электронной почтой {username} не зарегистрирован"
            )

        stmt = select(UserPassword.hashed_password).where(
            UserPassword.user_id == user.id
        )
        hashed_password: Optional[UserPassword] = (
            await session.execute(stmt)
        ).scalar_one_or_none()
        if hashed_password is None:
            raise NoResultFound(f"Пароль для пользователя с id {user.id} не найден")

        if not verify_password(password, hashed_password):
            return None
        return user

    # async def get_user_by_token(
    #         self, session: AsyncSession, token: str
    # ):
    #     # # This line also throws JWTError
    #     # payload = jwt.decode(
    #     #     token, settings.SECRET_KEY, algorithms=[settings.HASHING_ALGORITHM]
    #     # )
    #     # username = payload.get("sub")
    #     # if username is None:
    #     #     raise JWTError("Could not validate credentials")
    #     username = get_username_from_token(token)
    #
    #     # stmt = select(UserToken.user).where(UserToken.access_token == token).options(selectinload(UserToken.user))
    #     stmt = select(User).where(User.email == username)
    #     user: Optional[User] = (await session.execute(stmt)).scalar_one_or_none()
    #     if user is None:
    #         # raise NoResultFound(f"User with token {token} does not exist")
    #         raise JWTError("Could not validate credentials")
    #     return user

    async def create_user_token(
        self, session: AsyncSession, user_token_base: UserTokenBase
    ) -> UserToken:
        await User.by_id(session, user_token_base.user_id)
        await self.invalidate_old_tokens(session, user_token_base.user_id)
        user_token = await UserToken.create(session, user_token_base)
        return user_token

    async def create_user_password(
        self, session: AsyncSession, user_id: uuid.UUID, password: str
    ) -> bool:
        await User.by_id(session, user_id)
        hashed_password = get_password_hash(password)
        user_password = UserPassword(hashed_password=hashed_password, user_id=user_id)
        session.add(user_password)
        await session.commit()
        return True

    async def invalidate_old_tokens(
        self, session: AsyncSession, user_id: uuid.UUID
    ) -> None:
        """
        Invalidates only tokens that have expired refresh one
        So it's like a clean-up method for particular user
        """
        await User.by_id(session, user_id)
        stmt = (
            select(UserToken)
            .where(UserToken.user_id == user_id)
            .where(UserToken.is_valid == True)
        )
        tokens: list[UserToken] = (await session.execute(stmt)).scalars().all()

        for token in tokens:
            if token.refresh_expires_at <= datetime.now():
                token.is_valid = False
                session.add(token)

    async def invalidate_previous_token(
        self, session: AsyncSession, refresh_token: str
    ) -> None:
        """
        Invalidates previous pair of access and refresh tokens by given refresh token
        Should be called in refresh-token method
        """
        stmt = select(UserToken).where(UserToken.refresh_token == refresh_token)
        previous_token: Optional[UserToken] = (
            await session.execute(stmt)
        ).scalar_one_or_none()
        if previous_token is None:
            print("ALLERT, refresh token somehow was not found")
        else:
            previous_token.is_valid = False
            session.add(previous_token)

    async def is_token_valid(
        self, session: AsyncSession, token: str, token_kind: TokenKindOption
    ) -> bool:
        stmt = select(UserToken).where(UserToken.is_valid == True)
        if token_kind == TokenKindOption.access:
            stmt = stmt.where(UserToken.access_token == token)
        elif token_kind == TokenKindOption.refresh:
            stmt = stmt.where(UserToken.refresh_token == token)
        token_from_db: Optional[UserToken] = (
            await session.execute(stmt)
        ).scalar_one_or_none()

        if token_from_db is None:
            return False

        # I MUST NOT DISABLE A PAIR OF TOKENS IF ACCESS TOKEN IS EXPIRED CAUSE OTHERWISE REFRESH WON'T WORK
        if (
            token_kind == TokenKindOption.access
            and token_from_db.access_expires_at <= datetime.now()
        ):
            return False
        elif (
            token_kind == TokenKindOption.refresh
            and token_from_db.refresh_expires_at <= datetime.now()
        ):
            token_from_db.is_valid = False
            session.add(token_from_db)
            await session.commit()
            return False
        else:
            return True
