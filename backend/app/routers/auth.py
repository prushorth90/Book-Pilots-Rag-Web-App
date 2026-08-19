from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.security import decode_token
from app.database.session import get_db
from app.models.user import User
from app.repositories.users import get_user_by_id
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    TokenPair,
    UserCreate,
    UserResponse,
)
from app.services.auth import authenticate_user, refresh_access_token, register_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]) -> AuthResponse:
    return await register_user(db, data)


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest, db: Annotated[AsyncSession, Depends(get_db)]) -> AuthResponse:
    return await authenticate_user(db, str(data.email), data.password)


@router.post("/refresh", response_model=TokenPair)
async def refresh(data: RefreshRequest, db: Annotated[AsyncSession, Depends(get_db)]) -> TokenPair:
    try:
        user_id = decode_token(data.refresh_token, "refresh")
    except jwt.InvalidTokenError as error:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token") from error
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
    return refresh_access_token(user)


@router.get("/me", response_model=UserResponse)
async def me(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user
