from datetime import datetime

from aiogram import Router
from aiogram.filters.command import Command, CommandObject
from aiogram.types import Message

from app.users.dao.user_dao import UserDao
from app.users.models import User
from app.wishes.dao.wish_dao import WishDao
from app.wishes.dao.active_wish_dao import ActiveDao
from app.wishes.models import ActiveWish

active_router = Router()


@active_router.message(Command('doit'))
async def create_active_wish(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    if await check_active_wish(user):
        await get_active(user, message)
    else:
        await ActiveDao.create_active_wish(user)
        await get_active(user, message)


async def check_active_wish(user) -> bool:
    active_wish = await ActiveDao.get_active_wish_by_executor(user)
    if not active_wish:
        return False
    return True


async def get_active(user: User, message: Message):
    active_wish = await ActiveDao.get_active_wish_by_executor(user)
    if not active_wish:
        await message.answer('У вас еще нет активного желания')
        return
    await message.answer(
        f'Ваша желание: {active_wish.title}\n'
        f'Срок на выполнение:{active_wish.expired_at}\n'
    )


@active_router.message(Command('get_active_wish'))
async def get_active_wish(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    await get_active(user, message)


@active_router.message(Command('get_time'))
async def get_active_time(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    active_wish = await ActiveDao.get_active_wish_by_executor(user)
    if not active_wish:
        await message.answer('У вас еще нет активного желания')
        return

    days, hours, minutes = await get_time_until_expiration(active_wish.expired_at)
    await message.answer(
        f'Ваше желание: {active_wish.title}\n'
        f'Вам осталось {days} дней {hours} часов {minutes} минут до истечения срока.\n'
    )


async def get_time_until_expiration(expiration_date: datetime):
    now = datetime.now()
    # Разница между датой истечения срока и текущим временем
    time_delta = expiration_date - now
    # Преобразование разницы в дни, часы и минуты
    days = time_delta.days
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return days, hours, minutes
