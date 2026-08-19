from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import create_token, hash_password, verify_password
from app.models.user import User
from app.repositories.users import (
    create_user,
    get_user_by_email,
    get_user_by_username_or_email,
)
from app.schemas.auth import AuthResponse, TokenPair, UserCreate, UserResponse


def build_auth_response(user: User) -> AuthResponse:
    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=create_token(user.id, "access"),
        refresh_token=create_token(user.id, "refresh"),
    )


async def register_user(db: AsyncSession, data: UserCreate) -> AuthResponse:
    existing = await get_user_by_username_or_email(db, data.username, str(data.email))
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username or email already registered")
    try:
        user = await create_user(db, data, hash_password(data.password))
    except IntegrityError as error:
        await db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Username or email already registered"
        ) from error
    return build_auth_response(user)


async def authenticate_user(db: AsyncSession, email: str, password: str) -> AuthResponse:
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return build_auth_response(user)


def refresh_access_token(user: User) -> TokenPair:
    return TokenPair(
        access_token=create_token(user.id, "access"),
        refresh_token=create_token(user.id, "refresh"),
    )
