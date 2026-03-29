from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies import get_current_user_id
from app.schemas.chat import ChatRequest
from app.services.chat_service import chat_stream

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("/{session_id}")
async def chat(
    session_id: str,
    req: ChatRequest,
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_session)],
):
    return StreamingResponse(
        chat_stream(db, session_id, user_id, req.content),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
