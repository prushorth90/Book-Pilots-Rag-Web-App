from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.club import ClubBook, ClubBookStatus
from app.models.communication import ChatMessage, DiscussionPost, DiscussionThread


async def message_history(db: AsyncSession, club_id: int, limit: int) -> list[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.club_id == club_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    return list(reversed(result.unique().scalars().all()))


async def create_message(
    db: AsyncSession, club_id: int, sender_id: int, content: str
) -> ChatMessage:
    message = ChatMessage(club_id=club_id, sender_id=sender_id, content=content.strip())
    db.add(message)
    await db.commit()
    return await required_message(db, message.id)


async def get_message(db: AsyncSession, message_id: int) -> ChatMessage | None:
    result = await db.execute(select(ChatMessage).where(ChatMessage.id == message_id))
    return result.scalar_one_or_none()


async def edit_message(db: AsyncSession, message: ChatMessage, content: str) -> ChatMessage:
    message.content = content.strip()
    message.edited_at = datetime.now(UTC)
    await db.commit()
    return await required_message(db, message.id)


async def delete_message(db: AsyncSession, message: ChatMessage) -> ChatMessage:
    message.content = "Message removed"
    message.is_deleted = True
    message.edited_at = datetime.now(UTC)
    await db.commit()
    return await required_message(db, message.id)


async def current_book_id(db: AsyncSession, club_id: int) -> int | None:
    result = await db.execute(
        select(ClubBook.book_id).where(
            ClubBook.club_id == club_id, ClubBook.status == ClubBookStatus.CURRENT
        )
    )
    return result.scalar_one_or_none()


async def list_threads(db: AsyncSession, club_id: int, book_id: int) -> list[DiscussionThread]:
    result = await db.execute(
        select(DiscussionThread)
        .where(
            DiscussionThread.club_id == club_id,
            DiscussionThread.book_id == book_id,
        )
        .order_by(DiscussionThread.created_at.desc())
    )
    return list(result.unique().scalars())


async def create_thread(
    db: AsyncSession, club_id: int, book_id: int, creator_id: int, title: str
) -> DiscussionThread:
    thread = DiscussionThread(
        club_id=club_id, book_id=book_id, creator_id=creator_id, title=title.strip()
    )
    db.add(thread)
    await db.commit()
    return await required_thread(db, thread.id)


async def get_thread(db: AsyncSession, thread_id: int) -> DiscussionThread | None:
    result = await db.execute(select(DiscussionThread).where(DiscussionThread.id == thread_id))
    return result.unique().scalar_one_or_none()


async def create_post(
    db: AsyncSession,
    thread_id: int,
    author_id: int,
    content: str,
    parent_id: int | None,
) -> DiscussionPost:
    post = DiscussionPost(
        thread_id=thread_id,
        author_id=author_id,
        content=content.strip(),
        parent_id=parent_id,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def get_post(db: AsyncSession, post_id: int) -> DiscussionPost | None:
    result = await db.execute(select(DiscussionPost).where(DiscussionPost.id == post_id))
    return result.scalar_one_or_none()


async def edit_post(db: AsyncSession, post: DiscussionPost, content: str) -> DiscussionPost:
    post.content = content.strip()
    post.edited_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(post)
    return post


async def delete_post(db: AsyncSession, post: DiscussionPost) -> DiscussionPost:
    post.content = "Post removed"
    post.is_deleted = True
    post.edited_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(post)
    return post


async def required_message(db: AsyncSession, message_id: int) -> ChatMessage:
    message = await get_message(db, message_id)
    if message is None:
        raise RuntimeError("Message disappeared after persistence")
    return message


async def required_thread(db: AsyncSession, thread_id: int) -> DiscussionThread:
    thread = await get_thread(db, thread_id)
    if thread is None:
        raise RuntimeError("Thread disappeared after persistence")
    return thread
