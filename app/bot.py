import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, Message
from aiogram.utils.i18n import I18n, FSMI18nMiddleware, I18nMiddleware, SimpleI18nMiddleware  # noqa,
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings, DIR, setup_logging
from app.dao.user.pair_dao import PairDao
from app.dao.user.user_dao import UserDao
from app.dao.wish.active_wish_dao import ActiveDao
from app.routers.utils import reject_wish
from app.routers_utis import get_routers
from crypto.encryption_manager import decrypt as d

setup_logging()

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


async def alert_pair_request():
    await PairDao.delete_timeout_pair_request()


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
    scheduler.add_job(alert_timeout_active, 'interval', days=1)
    scheduler.add_job(alert_pair_request, 'interval', days=1)
    scheduler.start()

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
