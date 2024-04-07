import asyncio
import logging
from aiogram import Bot, types, Dispatcher, Router, F, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.enums.dice_emoji import DiceEmoji

from app.config import settings
from app.users.user_router import user_router
from app.base.bot_router import base_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.TOKEN)
dp = Dispatcher()

main_router = Router()
main_router.include_router(user_router)
main_router.include_router(base_router)
dp.include_router(main_router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
