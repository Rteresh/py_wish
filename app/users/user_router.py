from aiogram import types, Router
from aiogram.filters.command import Command
from aiogram.types import Message

from app.users.dao import create_user, get_user_by_id

user_router = Router()


@user_router.message(Command('register'))
async def bot_help(message: Message):
    data = message.from_user
    if await get_user_by_id(data.id):
        await message.answer(
            'Пользователь уже зарегистрирован!'
        )
    else:
        await create_user(data)
        await message.answer(
            'Пользователь успешно зарегистрирован!'
        )
