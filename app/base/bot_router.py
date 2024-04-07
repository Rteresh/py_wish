from aiogram import types, Router
from aiogram.filters.command import Command
from aiogram.types import Message

from app.users.dao import create_user, get_user_by_id

base_router = Router()


@base_router.message(Command('start'))
async def bot_help(message: Message):
    await message.answer(
        f'Привет, {message.from_user.first_name}!\n'
    )
