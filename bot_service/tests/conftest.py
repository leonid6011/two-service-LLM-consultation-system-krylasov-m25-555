import pytest
import pytest_asyncio
from fakeredis.aioredis import FakeRedis
from unittest.mock import patch


@pytest_asyncio.fixture
async def fake_redis():
    redis = FakeRedis()
    yield redis
    await redis.aclose()


@pytest.fixture(autouse=True)
def patch_redis(fake_redis):
    with patch("app.bot.handlers.get_redis", return_value=fake_redis):
        yield fake_redis
