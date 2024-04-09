from aiogram import types, Router
from aiogram.filters.command import Command
from aiogram.types import Message

from app.users.dao import create_user, get_user_by_id, get_my_pair, get_my_partner

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


@user_router.message(Command('my_pair'))
async def my_pair(message: Message):
    id: int = message.from_user.id
    pair = await get_my_pair(id)
    if pair:
        partner = await get_my_partner(id)
        await message.answer(
            f'Ваш партнер:{partner.username}'
        )
    else:
        await message.answer(
            'У вас еще нет партнера!'
        )


@user_router.message(Command('send'))
async def send(message: Message):
    await message.bot.send_message(chat_id=477542023, text=f'Сосать бояться')


