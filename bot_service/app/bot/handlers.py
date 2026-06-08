from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.jwt import decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()


@router.message(Command("token"))
async def cmd_token(message: Message) -> None:
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "Использование: /token <ваш_jwt_токен>\n"
            "Получите токен, зарегистрировавшись в Auth Service."
        )
        return

    token = parts[1].strip()

    try:
        decode_and_validate(token)
    except ValueError as e:
        await message.answer(
            f"Токен недействителен: {e}\n"
            "Пожалуйста, получите новый токен через Auth Service."
        )
        return

    redis = get_redis()
    await redis.set(f"tg_token:{message.from_user.id}", token, ex=86400)

    await message.answer("Токен сохранён. Теперь вы можете отправлять запросы к LLM.")


@router.message()
async def handle_text(message: Message) -> None:
    if not message.text:
        return

    redis = get_redis()
    token = await redis.get(f"tg_token:{message.from_user.id}")

    if not token:
        await message.answer(
            "Вы не авторизованы.\n"
            "Пожалуйста, отправьте команду /token <ваш_jwt_токен>\n"
            "Токен можно получить через Auth Service."
        )
        return

    if isinstance(token, bytes):
        token = token.decode()

    try:
        decode_and_validate(token)
    except ValueError as e:
        await redis.delete(f"tg_token:{message.from_user.id}")
        await message.answer(
            f"Ваш токен устарел или недействителен: {e}\n"
            "Пожалуйста, авторизуйтесь заново с помощью /token <новый_токен>."
        )
        return

    llm_request.delay(tg_chat_id=message.chat.id, prompt=message.text)
    await message.answer("Запрос принят, обрабатываю...")