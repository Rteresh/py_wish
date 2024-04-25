from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message

from app.users.dao.user_dao import UserDao
from app.users.dao.pair_dao import PairDao

pair_router = Router()


@pair_router.message(Command('cpp'))
async def bot_help(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    request = await PairDao.create_pair_request(user)
    await message.answer(
        f'Запрос создан {request}'
    )


@pair_router.message(Command('get_pair'))
async def get_pair(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    partner = await PairDao.get_my_partner(user)
    if not partner:
        await message.answer(
            'У вас еще нет партнера!'
        )
    else:
        await message.answer(
            f'Ваш партнер:{partner.username}'
        )
