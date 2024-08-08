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


@user_router.message(Command('send'))
async def send(message: Message):
    await message.bot.send_message(chat_id=477542023, text=_('Сосать бояться'))

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
