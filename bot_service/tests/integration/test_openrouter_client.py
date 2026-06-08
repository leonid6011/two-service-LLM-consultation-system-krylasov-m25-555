import pytest
import httpx

from app.services.openrouter_client import get_llm_response
from app.core.config import settings


@pytest.mark.respx(base_url=settings.OPENROUTER_BASE_URL)
async def test_get_llm_response_success(respx_mock):
    respx_mock.post("/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": "Лев Толстой родился в 1828 году."
                        }
                    }
                ]
            },
        )
    )

    result = await get_llm_response("Расскажи про Толстого")

    assert result == "Лев Толстой родился в 1828 году."
    assert respx_mock.calls.call_count == 1


@pytest.mark.respx(base_url=settings.OPENROUTER_BASE_URL)
async def test_get_llm_response_non_200(respx_mock):
    respx_mock.post("/chat/completions").mock(
        return_value=httpx.Response(429, json={"error": "rate limited"})
    )

    with pytest.raises(RuntimeError, match="429"):
        await get_llm_response("Какой-то запрос")


@pytest.mark.respx(base_url=settings.OPENROUTER_BASE_URL)
async def test_get_llm_response_network_error(respx_mock):
    respx_mock.post("/chat/completions").mock(
        side_effect=httpx.RequestError("connection failed")
    )

    with pytest.raises(RuntimeError, match="Network error"):
        await get_llm_response("Какой-то запрос")
