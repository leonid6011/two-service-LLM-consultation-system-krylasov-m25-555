import asyncio

from aiogram import Bot

from app.core.config import settings
from app.infra.celery_app import celery_app
from app.services.llm_client import get_llm_response


@celery_app.task(name="app.tasks.llm_tasks.llm_request", bind=True, max_retries=3)
def llm_request(self, tg_chat_id: int, prompt: str) -> None:
    try:
        response_text = asyncio.run(get_llm_response(prompt))

        async def _send_message() -> None:
            bot = Bot(token=settings.BOT_TOKEN)
            try:
                await bot.send_message(chat_id=tg_chat_id, text=response_text)
            finally:
                await bot.session.close()

        asyncio.run(_send_message())

    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)