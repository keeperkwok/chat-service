from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session as get_db
from app.dependencies import get_current_user_id
from app.schemas.session import SessionCreate, SessionUpdate, SessionOut, SessionDetailOut, MessageOut
from app.services import session_service, chat_service

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.post("", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
async def create_session(
    req: SessionCreate,
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await session_service.create_session(db, user_id, req)


@router.get("", response_model=list[SessionOut])
async def list_sessions(
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await session_service.list_sessions(db, user_id)


@router.get("/{session_id}", response_model=SessionDetailOut)
async def get_session(
    session_id: str,
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    chat_session, messages = await session_service.get_session_with_messages(db, session_id, user_id)
    return SessionDetailOut(
        **SessionOut.model_validate(chat_session).model_dump(),
        messages=[MessageOut.model_validate(m) for m in messages],
    )


@router.put("/{session_id}", response_model=SessionOut)
async def update_session(
    session_id: str,
    req: SessionUpdate,
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await session_service.update_session_title(db, session_id, user_id, req)


@router.post("/{session_id}/generate-title", response_model=SessionOut)
async def generate_session_title(
    session_id: str,
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await chat_service.generate_title(db, session_id, user_id)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await session_service.delete_session(db, session_id, user_id)
