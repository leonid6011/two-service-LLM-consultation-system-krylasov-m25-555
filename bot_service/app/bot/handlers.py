from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.jwt import decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    redis = get_redis()
    token = await redis.get(f"tg_token:{message.from_user.id}")

    if not token:
        await message.answer(
            "Вы не авторизованы.\n"
            "Это бот с доступом к языковой модели по JWT-токену.\n"
            "Сначала получите JWT в Auth Service, затем отправьте его командой:\n"
            "/token <ваш_jwt_токен>\n"
            "После этого просто напишите вопрос."
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
            "Пожалуйста, получите новый JWT в Auth Service и отправьте его командой:\n"
            "/token <новый_токен>"
        )
        return

    await message.answer(
        "Вы уже авторизованы.\n"
        "Можете отправить вопрос."
    )


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

    await message.answer("Токен сохранён. Теперь можно отправлять запросы модели.")


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
    await message.answer("Запрос принят. Ответ придёт следующим сообщением.")