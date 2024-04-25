import asyncio
import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.types import BotCommand

from app.config import settings
from app.users.router.user_router import user_router
from app.base.base_router import base_router
from app.wishes.router.wish_routers import wish_router
from app.users.router.pair_router import pair_router
from app.base.menu.menu_router import menu_router
from app.wishes.router.active_wish_router import active_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.TOKEN)
dp = Dispatcher()

main_router = Router()
main_router.include_router(user_router)
main_router.include_router(base_router)
main_router.include_router(wish_router)
main_router.include_router(pair_router)
main_router.include_router(menu_router)
main_router.include_router(active_router)
dp.include_router(main_router)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начать"),
        BotCommand(command="cpp", description="Создать ссылку на пару"),
        BotCommand(command="get_pair", description="Посмотреть на своего партнера"),
        BotCommand(command="add_wish", description="Добавить желание"),
        BotCommand(command="doit", description="Хочу выполнить желание партнера"),
        BotCommand(command="add_active_wish", description="Добавить активное желание"),
        BotCommand(command="get_active_wish", description="Посмотреть активное желание"),
        BotCommand(command="get_all_wishes", description="Посмотреть все мои желания"),
        BotCommand(command="get_time", description="Посмотреть оставшиеся время"),
    ]
    await bot.set_my_commands(commands)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
    asyncio.run(set_commands(bot))
