import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.utils.i18n import I18n, ConstI18nMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings, DIR
from app.dao.user.user_dao import UserDao
from app.dao.wish.active_wish_dao import ActiveDao
from app.routers_utis import get_routers

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.TOKEN)
dp = Dispatcher()

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

dp.include_router(get_routers())


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начать"),
        BotCommand(command="create_pair", description="Создать запрос на пару"),
        BotCommand(command="get_pair", description="Посмотреть на своего партнера"),
        BotCommand(command="reject_pair", description="Отклонить текущего партнера"),
        BotCommand(command="add_wish", description="Добавить желание"),
        BotCommand(command="doit", description="Хочу выполнить желание партнера"),
        BotCommand(command="add_active_wish", description="Добавить активное желание"),
        BotCommand(command="get_active_wish", description="Посмотреть активное желание"),
        BotCommand(command="get_all_wishes", description="Посмотреть все мои желания"),
        BotCommand(command="get_time", description="Посмотреть оставшиеся время"),
        BotCommand(command="done", description="Выполнил желание партнера"),
    ]
    await bot.set_my_commands(commands)


async def alert_timeout_active():
    active_wishes = await ActiveDao.get_all_unfulfilled_wish()
    for active_wish in active_wishes:
        owner = await UserDao.find_one_or_none(id=active_wish.owner_id)
        executor = await UserDao.find_one_or_none(id=active_wish.executor_id)
        await bot.send_message(owner.id, f"Ваше желание {active_wish.title} не выполнено,\n"
                                         f" партнером:{executor.username}. ")
        await ActiveDao.reject_active_wish(executor)
        print('well done')


i18n = I18n(path=DIR / 'locales', default_locale='ru', domain='messages')

i18n_middleware = ConstI18nMiddleware(i18n=i18n, locale='ru')
dp.update.middleware(i18n_middleware)


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
