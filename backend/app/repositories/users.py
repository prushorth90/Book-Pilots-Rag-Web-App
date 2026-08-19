from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import UserCreate


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


async def get_user_by_username_or_email(db: AsyncSession, username: str, email: str) -> User | None:
    result = await db.execute(
        select(User).where(or_(User.username == username, User.email == email.lower()))
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, data: UserCreate, password_hash: str) -> User:
    user = User(
        username=data.username,
        email=data.email.lower(),
        password_hash=password_hash,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
