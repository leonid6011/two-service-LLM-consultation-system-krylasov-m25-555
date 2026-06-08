from typing import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidTokenError, TokenExpiredError
from app.core.security import decode_token
from app.db.models import User
from app.db.session import AsyncSessionLocal
from app.repositories.users import UserRepository
from app.usecases.auth import AuthUseCase

bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_users_repo(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)


def get_auth_uc(repo: UserRepository = Depends(get_users_repo)) -> AuthUseCase:
    return AuthUseCase(repo)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> int:
    if not credentials:
        raise InvalidTokenError()

    token = credentials.credentials
    try:
        payload = decode_token(token)
    except ValueError as e:
        if "expired" in str(e).lower():
            raise TokenExpiredError()
        raise InvalidTokenError()

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenError()

    return int(user_id)


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    auth_uc: AuthUseCase = Depends(get_auth_uc),
) -> User:
    return await auth_uc.me(user_id)
