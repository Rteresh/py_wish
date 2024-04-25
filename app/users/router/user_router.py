from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message

from app.users.dao.user_dao import UserDao
from app.users.dao.pair_dao import PairDao

user_router = Router()


@user_router.message(Command('my_pair'))
async def my_pair(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    pair = await PairDao.get_my_pair(user=user)
    if pair:
        partner = await PairDao.get_my_pair(user)
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
