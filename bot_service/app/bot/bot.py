import asyncio

from app.bot.dispatcher import bot, dp


async def start_bot() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(dp.start_polling(bot))


async def stop_bot() -> None:
    await dp.stop_polling()
    await bot.session.close()
