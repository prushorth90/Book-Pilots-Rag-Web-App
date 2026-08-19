import json
from collections import defaultdict
from typing import Annotated

import jwt
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.auth.club_permissions import get_club_membership, require_moderator, require_participant
from app.auth.security import decode_token
from app.database.session import SessionLocal, get_db
from app.models.communication import ChatMessage
from app.models.user import User
from app.repositories import communication as repository
from app.repositories.users import get_user_by_id
from app.schemas.communication import (
    MessageCreate,
    MessageResponse,
    PostCreate,
    PostResponse,
    ThreadCreate,
    ThreadResponse,
)

router = APIRouter(tags=["club communication"])
Db = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


class ClubConnectionManager:
    def __init__(self) -> None:
        self.connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, club_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[club_id].add(websocket)

    def disconnect(self, club_id: int, websocket: WebSocket) -> None:
        self.connections[club_id].discard(websocket)

    async def broadcast(self, club_id: int, payload: dict[str, object]) -> None:
        stale: list[WebSocket] = []
        for connection in self.connections[club_id]:
            try:
                await connection.send_json(payload)
            except RuntimeError:
                stale.append(connection)
        for connection in stale:
            self.disconnect(club_id, connection)


connections = ClubConnectionManager()


def message_payload(message: ChatMessage) -> dict[str, object]:
    body = MessageResponse.model_validate(message).model_dump(mode="json")
    return {"type": "message", "message": body}


async def required_message(db: AsyncSession, club_id: int, message_id: int) -> ChatMessage:
    message = await repository.get_message(db, message_id)
    if not message or message.club_id != club_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Message not found")
    return message


@router.get("/clubs/{club_id}/messages", response_model=list[MessageResponse])
async def history(
    club_id: int,
    db: Db,
    user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> list[MessageResponse]:
    await require_participant(db, club_id, user.id)
    return [
        MessageResponse.model_validate(item)
        for item in await repository.message_history(db, club_id, limit)
    ]


@router.patch("/clubs/{club_id}/messages/{message_id}", response_model=MessageResponse)
async def edit_chat_message(
    club_id: int, message_id: int, data: MessageCreate, db: Db, user: CurrentUser
) -> MessageResponse:
    await require_participant(db, club_id, user.id)
    message = await required_message(db, club_id, message_id)
    if message.sender_id != user.id or message.is_deleted:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the sender can edit this message")
    updated = await repository.edit_message(db, message, data.content)
    await connections.broadcast(
        club_id,
        {
            "type": "message_updated",
            "message": MessageResponse.model_validate(updated).model_dump(mode="json"),
        },
    )
    return MessageResponse.model_validate(updated)


@router.delete("/clubs/{club_id}/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_message(club_id: int, message_id: int, db: Db, user: CurrentUser) -> Response:
    await require_participant(db, club_id, user.id)
    message = await required_message(db, club_id, message_id)
    if message.sender_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the sender can delete this message")
    deleted = await repository.delete_message(db, message)
    await connections.broadcast(
        club_id,
        {
            "type": "message_deleted",
            "message": MessageResponse.model_validate(deleted).model_dump(mode="json"),
        },
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/clubs/{club_id}/moderation/messages/{message_id}", response_model=MessageResponse)
async def moderate_message(
    club_id: int, message_id: int, db: Db, user: CurrentUser
) -> MessageResponse:
    await require_moderator(db, club_id, user.id)
    message = await required_message(db, club_id, message_id)
    deleted = await repository.delete_message(db, message)
    await connections.broadcast(
        club_id,
        {
            "type": "message_deleted",
            "message": MessageResponse.model_validate(deleted).model_dump(mode="json"),
        },
    )
    return MessageResponse.model_validate(deleted)


@router.get("/clubs/{club_id}/discussions", response_model=list[ThreadResponse])
async def discussions(club_id: int, db: Db, user: CurrentUser) -> list[ThreadResponse]:
    await require_participant(db, club_id, user.id)
    book_id = await repository.current_book_id(db, club_id)
    if book_id is None:
        return []
    return [
        ThreadResponse.model_validate(item)
        for item in await repository.list_threads(db, club_id, book_id)
    ]


@router.post("/clubs/{club_id}/discussions", response_model=ThreadResponse, status_code=201)
async def create_discussion(
    club_id: int, data: ThreadCreate, db: Db, user: CurrentUser
) -> ThreadResponse:
    await require_participant(db, club_id, user.id)
    book_id = await repository.current_book_id(db, club_id)
    if book_id is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Select a current club book first")
    return ThreadResponse.model_validate(
        await repository.create_thread(db, club_id, book_id, user.id, data.title)
    )


@router.post(
    "/clubs/{club_id}/discussions/{thread_id}/posts", response_model=PostResponse, status_code=201
)
async def create_discussion_post(
    club_id: int, thread_id: int, data: PostCreate, db: Db, user: CurrentUser
) -> PostResponse:
    await require_participant(db, club_id, user.id)
    thread = await repository.get_thread(db, thread_id)
    if not thread or thread.club_id != club_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Discussion not found")
    if data.parent_id:
        parent = await repository.get_post(db, data.parent_id)
        if not parent or parent.thread_id != thread_id:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid parent post")
    return PostResponse.model_validate(
        await repository.create_post(db, thread_id, user.id, data.content, data.parent_id)
    )


@router.patch("/clubs/{club_id}/discussions/posts/{post_id}", response_model=PostResponse)
async def edit_discussion_post(
    club_id: int, post_id: int, data: MessageCreate, db: Db, user: CurrentUser
) -> PostResponse:
    await require_participant(db, club_id, user.id)
    post = await repository.get_post(db, post_id)
    thread = await repository.get_thread(db, post.thread_id) if post else None
    if (
        not post
        or not thread
        or thread.club_id != club_id
        or post.author_id != user.id
        or post.is_deleted
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the author can edit this post")
    return PostResponse.model_validate(await repository.edit_post(db, post, data.content))


@router.delete("/clubs/{club_id}/discussions/posts/{post_id}", status_code=204)
async def delete_discussion_post(club_id: int, post_id: int, db: Db, user: CurrentUser) -> Response:
    await require_participant(db, club_id, user.id)
    post = await repository.get_post(db, post_id)
    thread = await repository.get_thread(db, post.thread_id) if post else None
    if not post or not thread or thread.club_id != club_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    if post.author_id != user.id:
        await require_moderator(db, club_id, user.id)
    await repository.delete_post(db, post)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.websocket("/ws/clubs/{club_id}")
async def club_chat(websocket: WebSocket, club_id: int, token: str = Query()) -> None:
    try:
        user_id = decode_token(token, "access")
    except jwt.InvalidTokenError:
        await websocket.close(code=4401, reason="Invalid access token")
        return
    async with SessionLocal() as db:
        user = await get_user_by_id(db, user_id)
        membership = await get_club_membership(db, club_id, user_id)
        if not user or not membership:
            await websocket.close(code=4403, reason="Club membership required")
            return
    await connections.connect(club_id, websocket)
    await websocket.send_json({"type": "connected", "club_id": club_id})
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                payload = json.loads(raw)
                content = MessageCreate.model_validate(payload).content
            except (json.JSONDecodeError, ValueError):
                await websocket.send_json({"type": "error", "detail": "Invalid message"})
                continue
            async with SessionLocal() as db:
                message = await repository.create_message(db, club_id, user_id, content)
                event = message_payload(message)
            await connections.broadcast(club_id, event)
    except WebSocketDisconnect:
        connections.disconnect(club_id, websocket)
