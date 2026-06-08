from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.bot.bot import start_bot, stop_bot


@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_bot()
    yield
    await stop_bot()


app = FastAPI(
    title="Bot Service",
    description="Telegram bot service with LLM consultations",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}
