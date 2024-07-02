from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message

from app.dao.user.user_dao import UserDao
from app.dao.user.pair_dao import PairDao

pair_router = Router()


@pair_router.message(Command('create_pair'))
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


@pair_router.message(Command('reject_pair'))
async def reject_pair(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    pair = await PairDao.get_my_pair(user)
    if not pair:
        await message.answer(
            'У вас еще нет партнера!'
        )
    else:
        await PairDao.delete_my_pair(user)
        await message.answer(
            f'Вы больше не являетесь партнерами!'
        )
