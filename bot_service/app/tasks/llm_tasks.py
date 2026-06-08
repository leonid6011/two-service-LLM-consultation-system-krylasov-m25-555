import asyncio

from app.infra.celery_app import celery_app
from app.infra.redis import get_redis
from app.services.llm_client import get_llm_response


@celery_app.task(name="app.tasks.llm_tasks.llm_request", bind=True, max_retries=3)
def llm_request(self, tg_chat_id: int, prompt: str) -> None:
    try:
        response_text = asyncio.run(get_llm_response(prompt))

        async def _save():
            redis = get_redis()
            await redis.set(f"llm_result:{tg_chat_id}", response_text, ex=300)

        asyncio.run(_save())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
