import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import BotCommand, Message
from aiogram.utils.i18n import I18n, ConstI18nMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings, DIR
from app.dao.user.user_dao import UserDao
from app.dao.wish.active_wish_dao import ActiveDao
from app.routers.utils import reject_wish
from app.routers_utis import get_routers
from crypto.encryption_manager import decrypt as d

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.TOKEN)
dp = Dispatcher()

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

dp.include_router(get_routers())


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="menu", description="Menu")
    ]
    await bot.set_my_commands(commands)


async def alert_timeout_active():
    active_wishes = await ActiveDao.get_all_unfulfilled_wish()
    for active_wish in active_wishes:
        owner = await UserDao.find_one_or_none(id=active_wish.owner_id)
        executor = await UserDao.find_one_or_none(id=active_wish.executor_id)
        await bot.send_message(owner.id, f"Ваше желание {d(active_wish.title)} не выполнено,\n"
                                         f" партнером:{executor.username}. ")

        # Поправляем в бд
        await reject_wish(
            active_wish=active_wish,
            user=executor
        )


i18n = I18n(path=DIR / 'locales', default_locale='en', domain='messages')

i18n_middleware = ConstI18nMiddleware(i18n=i18n, locale='en')
dp.update.middleware(i18n_middleware)


@dp.message(Command('ru'))
async def set_language_ru(message: Message):
    user_id = message.from_user.id
    await UserDao.update_language(user_id=user_id, new_language='ru')

    # Apply the new language
    i18n.ctx_locale.set('ru')

    # Send confirmation to the user
    await message.answer("Основной язык изменен на русский.")


@dp.message(Command('en'))
async def set_language_en(message: Message):
    user_id = message.from_user.id
    await UserDao.update_language(user_id=user_id, new_language='en')

    # Apply the new language
    i18n.ctx_locale.set('en')

    # Send confirmation to the user
    await message.answer("Main language changed to English.")


async def main():
    logging.info("Starting bot...")
    await set_commands(bot)
    scheduler.add_job(alert_timeout_active, 'interval', days=1)
    scheduler.start()

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
