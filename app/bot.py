import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, Message
from aiogram.utils.i18n import I18n, FSMI18nMiddleware, I18nMiddleware, SimpleI18nMiddleware  # noqa,

from app.config import settings, DIR, setup_logging
from app.routers_utis import get_routers
from app.utils.job_scheduler.jobs import scheduler_run

setup_logging()

bot = Bot(token=settings.TOKEN)
dp = Dispatcher()

dp.include_router(get_routers())


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="menu", description="Menu")
    ]
    await bot.set_my_commands(commands)


i18n = I18n(path=DIR / 'locales', default_locale='ru', domain='messages')

i18n_middleware = FSMI18nMiddleware(i18n=i18n)
dp.update.middleware(i18n_middleware)


@dp.message(F.contains('en'))
async def lag1(message: Message, state: FSMContext):
    await i18n_middleware.set_locale(state=state, locale='en')
    await message.answer('en язык')


@dp.message(F.contains('ru'))
async def lag1(message: Message, state: FSMContext):
    await i18n_middleware.set_locale(state=state, locale='ru')
    await message.answer('ru язык')


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
