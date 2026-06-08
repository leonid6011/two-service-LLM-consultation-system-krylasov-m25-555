import httpx

from app.core.config import settings


async def get_llm_response(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [
            {"role": "user", "content": prompt},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"OpenRouter returned status {response.status_code}: {response.text}"
            )

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except httpx.RequestError as exc:
        raise RuntimeError(f"Network error when calling OpenRouter: {exc}") from exc
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Unexpected OpenRouter response format: {exc}") from exc
