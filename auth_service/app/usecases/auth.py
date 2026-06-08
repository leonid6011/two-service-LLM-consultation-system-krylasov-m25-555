from app.core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.models import User
from app.repositories.users import UserRepository


class AuthUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register(self, email: str, password: str) -> User:
        existing = await self.repository.get_by_email(email)
        if existing:
            raise UserAlreadyExistsError()

        password_hash = hash_password(password)
        user = await self.repository.create(email=email, password_hash=password_hash)
        return user

    async def login(self, email: str, password: str) -> str:
        user = await self.repository.get_by_email(email)
        if not user:
            raise InvalidCredentialsError()

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        token = create_access_token(sub=str(user.id), role=user.role)
        return token

    async def me(self, user_id: int) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user
