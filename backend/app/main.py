from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database.base import Base
from app.database.session import engine
from app.models import (  # noqa: F401
    Book,
    BookClub,
    BookClubMember,
    ClubBook,
    Meeting,
    MeetingAttendee,
    User,
    UserAvailability,
    UserBook,
    UserGenre,
    WeeklyAvailability,
)
from app.routers.auth import router as auth_router
from app.routers.books import router as books_router
from app.routers.clubs import router as clubs_router
from app.routers.health import router as health_router
from app.routers.meetings import router as meetings_router
from app.routers.recommendations import router as recommendations_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(books_router)
app.include_router(recommendations_router)
app.include_router(clubs_router)
app.include_router(meetings_router)
