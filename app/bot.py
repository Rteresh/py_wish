import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.utils.i18n import I18n, FSMI18nMiddleware, I18nMiddleware, SimpleI18nMiddleware  # noqa,

from app.config import settings, setup_logging
from app.routers.menu.language_router import i18n_middleware
from app.routers_utis import get_routers
from app.utils.job_scheduler.jobs import scheduler_run

setup_logging()

bot = Bot(token=settings.TOKEN)
dp = Dispatcher()

dp.include_router(get_routers())
dp.update.middleware(i18n_middleware)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="menu", description="Menu")
    ]
    await bot.set_my_commands(commands)


async def main():
    logging.info("Starting bot...")
    await set_commands(bot)
    await scheduler_run(bot)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
