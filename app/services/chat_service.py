import json
from typing import AsyncGenerator

from fastapi import HTTPException, status
from openai import AsyncAzureOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.session import ChatSession
from app.models.message import ChatMessage, MessageRole

_client = AsyncAzureOpenAI(
    api_key=settings.azure_openai_api_key,
    azure_endpoint=settings.azure_openai_endpoint,
    api_version=settings.azure_openai_api_version,
)


async def _assert_session_owner(db: AsyncSession, session_id: str, user_id: int) -> ChatSession:
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    chat_session = result.scalar_one_or_none()
    if not chat_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if chat_session.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return chat_session


async def chat_stream(
    db: AsyncSession,
    session_id: str,
    user_id: int,
    user_content: str,
) -> AsyncGenerator[str, None]:
    chat_session = await _assert_session_owner(db, session_id, user_id)

    # Save user message
    user_msg = ChatMessage(
        session_id=session_id,
        role=MessageRole.user,
        content=user_content,
    )
    db.add(user_msg)
    await db.commit()

    # Load full history for context
    history_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id.asc())
    )
    history = history_result.scalars().all()

    messages = [{"role": msg.role.value, "content": msg.content} for msg in history]

    # Stream from Azure OpenAI
    full_reply = ""
    try:
        stream = await _client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=messages,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                full_reply += delta
                yield f"data: {json.dumps({'delta': delta}, ensure_ascii=False)}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"
        return

    yield "data: [DONE]\n\n"

    # Save assistant reply and touch session.updated_at

    assistant_msg = ChatMessage(
        session_id=session_id,
        role=MessageRole.assistant,
        content=full_reply,
    )
    db.add(assistant_msg)
    # ON UPDATE CURRENT_TIMESTAMP triggers on any column change
    await db.execute(
        ChatSession.__table__.update()
        .where(ChatSession.id == session_id)
        .values(title=chat_session.title)
    )
    await db.commit()


async def generate_title(
    db: AsyncSession,
    session_id: str,
    user_id: int,
) -> ChatSession:
    chat_session = await _assert_session_owner(db, session_id, user_id)

    # Fetch the first user message for context
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id, ChatMessage.role == MessageRole.user)
        .order_by(ChatMessage.id.asc())
        .limit(1)
    )
    first_msg = result.scalar_one_or_none()
    if not first_msg:
        return chat_session

    try:
        response = await _client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "请根据用户的问题，用不超过20个字生成一个简洁的会话标题。"
                        "直接输出标题文字，不加引号、序号或任何标点符号。"
                    ),
                },
                {"role": "user", "content": first_msg.content},
            ],
            max_tokens=40,
            stream=False,
        )
        title = response.choices[0].message.content.strip()
        if title:
            chat_session.title = title
            await db.commit()
            await db.refresh(chat_session)
    except Exception:
        pass  # Keep existing title on error

    return chat_session
