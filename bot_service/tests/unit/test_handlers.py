from unittest.mock import AsyncMock, MagicMock, patch
import jwt as pyjwt
from datetime import datetime, timedelta, timezone

from app.core.config import settings


def make_valid_token(sub: str = "42", role: str = "user") -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=30)).timestamp()),
    }
    return pyjwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def make_message(text: str, user_id: int = 123, chat_id: int = 123) -> MagicMock:
    message = MagicMock()
    message.text = text
    message.from_user = MagicMock()
    message.from_user.id = user_id
    message.chat = MagicMock()
    message.chat.id = chat_id
    message.answer = AsyncMock()
    return message


async def test_cmd_token_saves_valid_token(patch_redis):
    from app.bot.handlers import cmd_token

    token = make_valid_token()
    message = make_message(f"/token {token}")

    await cmd_token(message)

    saved = await patch_redis.get(f"tg_token:{message.from_user.id}")
    if isinstance(saved, bytes):
        saved = saved.decode()
    assert saved == token
    message.answer.assert_called_once()
    assert "сохранён" in message.answer.call_args[0][0].lower()


async def test_cmd_token_rejects_invalid_token(patch_redis):
    from app.bot.handlers import cmd_token

    message = make_message("/token this.is.invalid")

    await cmd_token(message)

    saved = await patch_redis.get(f"tg_token:{message.from_user.id}")
    assert saved is None
    message.answer.assert_called_once()
    assert "недействителен" in message.answer.call_args[0][0].lower()


async def test_handle_text_no_token(patch_redis):
    from app.bot.handlers import handle_text

    message = make_message("Привет, кто такой Толстой?")

    await handle_text(message)

    message.answer.assert_called_once()
    assert "авторизованы" in message.answer.call_args[0][0].lower()


async def test_handle_text_with_valid_token_calls_celery(patch_redis):
    from app.bot.handlers import handle_text

    token = make_valid_token()
    await patch_redis.set("tg_token:123", token)

    message = make_message("Расскажи про Толстого", user_id=123, chat_id=123)

    with patch("app.bot.handlers.llm_request") as mock_task:
        mock_delay = MagicMock()
        mock_task.delay = mock_delay

        await handle_text(message)

        mock_delay.assert_called_once_with(
            tg_chat_id=123,
            prompt="Расскажи про Толстого",
        )

    message.answer.assert_called_once()
    assert "принят" in message.answer.call_args[0][0].lower()
