from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from app.dao.user.pair_dao import PairDao
from app.dao.user.user_dao import UserDao

user_router = Router()


@user_router.message(Command('my_pair'))
async def my_pair(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    pair = await PairDao.get_my_pair(user=user)
    if pair:
        partner = await PairDao.get_my_pair(user)
        await message.answer(
            _('Ваш партнер:{partner}').format(partner=partner.username)
        )
    else:
        await message.answer(
            _('У вас еще нет партнера!')
        )


@user_router.message(Command('lag1'))
async def lag1(message: Message):
    await message.answer(f'Ваш язык {await UserDao.get_language(message.from_user.id)}')


@user_router.message(Command('lag2'))
async def lag1(message: Message):
    user_id = message.from_user.id
    await UserDao.update_language(user_id=user_id, new_language='en')
    await message.answer(f'Ваш язык {await UserDao.get_language(user_id)}')


@user_router.message(Command('lag3'))
async def lag1(message: Message):
    user_id = message.from_user.id
    await UserDao.update_language(user_id=user_id, new_language='ru')
    await message.answer(f'Ваш язык {await UserDao.get_language(user_id)}')


# PREMIUM HERE !!!!!
# @user_router.message(Command('tree'))
# async def is_premium(message: Message):
#     user = await UserDao.find_one_or_none(id=message.from_user.id)
#     if user.is_premium:
#         await message.answer('У тебя премиум')
#     else:
#         await message.answer('У тебя нет премиума')
#
#
# @user_router.message(Command('traa'))
# async def is_premium(message: Message):
#     user = await UserDao.find_one_or_none(id=message.from_user.id)
#     await UserDao.update_premium(user, True)
