import uuid

from fastapi import HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import ChatSession
from app.models.message import ChatMessage
from app.schemas.session import SessionCreate, SessionUpdate


async def create_session(session: AsyncSession, user_id: int, req: SessionCreate) -> ChatSession:
    chat_session = ChatSession(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=req.title or "新对话",
    )
    session.add(chat_session)
    await session.commit()
    await session.refresh(chat_session)
    return chat_session


async def list_sessions(session: AsyncSession, user_id: int) -> list[ChatSession]:
    result = await session.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .order_by(ChatSession.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_session_with_messages(
    session: AsyncSession, session_id: str, user_id: int
) -> tuple[ChatSession, list[ChatMessage]]:
    result = await session.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    chat_session = result.scalar_one_or_none()
    if not chat_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if chat_session.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    msg_result = await session.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id.asc())
    )
    messages = list(msg_result.scalars().all())
    return chat_session, messages


async def update_session_title(
    session: AsyncSession, session_id: str, user_id: int, req: SessionUpdate
) -> ChatSession:
    result = await session.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    chat_session = result.scalar_one_or_none()
    if not chat_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if chat_session.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    chat_session.title = req.title
    await session.commit()
    await session.refresh(chat_session)
    return chat_session


async def delete_session(session: AsyncSession, session_id: str, user_id: int) -> None:
    result = await session.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    chat_session = result.scalar_one_or_none()
    if not chat_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if chat_session.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    await session.execute(delete(ChatMessage).where(ChatMessage.session_id == session_id))
    await session.execute(delete(ChatSession).where(ChatSession.id == session_id))
    await session.commit()
