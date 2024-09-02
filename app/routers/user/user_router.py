from datetime import datetime

from aiogram import Router
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from app.config import settings
from app.dao.user.pair_dao import PairDao
from app.dao.user.user_dao import UserDao
from app.models.user.models import User

user_router = Router()


async def my_pair(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    pair = await PairDao.get_my_pair(user=user)
    if pair:
        partner = await PairDao.get_partner(user)
        await message.answer(
            _('Ваш партнер:{partner}').format(partner=partner.username)
        )
    else:
        await message.answer(
            _('У вас еще нет партнера!')
        )


async def _update_premium_test_period(message: Message, user: User):
    """
    Обновляет статус премиум пользователя.
    :param user: Модель пользователя
    :param message:
    :return:
    """
    time = settings.TEST_PERIOD_PREMIUM
    if user.test_premium:
        await UserDao.update_premium(user, True, time)
        await message.answer(_('Пробный период подписки на 1 месяц активирован!'))
        await UserDao.update_test_premium(user, False)
    else:
        await message.answer(_('Пробный период подписки уже был активирован!'))


async def _update_premium(message: Message, user: User, time: int):
    """
    Обновляет статус премиум пользователя.
    :param user: Модель пользователя
    :param time: Кол-во месяцев подписки
    :param message:
    :return:
    """
    await UserDao.update_premium(user, True, time)
    await message.answer(_('Премиум на 12 месяцев активирован!'))


async def update_premium(message: Message):
    """
    Обновляет статус премиум пользователя.
    :param message:
    :return:
    """
    user = await UserDao.find_by_id(model_id=message.from_user.id)

    if user.test_premium:
        await _update_premium_test_period(message, user)
    else:
        await message.answer(_('Скоро будет платная подписка'))
        # ЗАГЛУШКА ДЛЯ ПОСЛЕДУБЩЕЙ РЕАЛИЗАЦИИ ПОДПИСКИ


async def get_premium_status(message: Message):
    """
    Выводит статус премиум пользователя.
    :param message:
    :return:
    """
    user = await UserDao.find_by_id(model_id=message.from_user.id)
    if user.is_premium:
        await message.answer(await _get_premium_time(user))
    else:
        await message.answer(_('У вас нет премиума'))


async def _get_premium_time(user: User) -> str:
    """
    Формирует текстовую информацию о времени, оставшемся до истечения подписки .

    :param user: Объект User.
    :return: Строка с информацией о желании и времени до его истечения.
    """
    days, hours, minutes = await _get_time_until_expiration(user.time_premium)

    if days < 0:
        text = _("Премиум подписка закончилась")
    else:
        text = _("Осталось {days} дней {hours} часов {minutes} минут до истечения срока подписки.\n").format(
            days=days,
            hours=hours,
            minutes=minutes)
    return text


async def _get_time_until_expiration(time_premium: datetime) -> tuple[int, int, int]:
    """
    Вычисляет и возвращает время до истечения срока подписки в днях, часах и минутах.

    :param time_premium: Дата и время истечения срока желания.
    :return: Кортеж, содержащий количество дней, часов и минут до истечения срока.
    """
    now = datetime.now()
    time_delta = time_premium - now
    days = time_delta.days
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return days, hours, minutes

# @user_router.message(Command('lag1'))
# async def lag1(message: Message):
#     await message.answer(f'Ваш язык {await UserDao.get_language(message.from_user.id)}')
#
#
# @user_router.message(Command('lag2'))
# async def lag1(message: Message):
#     user_id = message.from_user.id
#     await UserDao.update_language(user_id=user_id, new_language='en')
#
#     await message.answer(f'Ваш язык {await UserDao.get_language(user_id)}')
#

# @user_router.message(Command('lag3'))
# async def lag1(message: Message):
#     user_id = message.from_user.id
#     await UserDao.update_language(user_id=user_id, new_language='ru')
#     await message.answer(f'Ваш язык {await UserDao.get_language(user_id)}')
#
#
# # PREMIUM HERE !!!!!
# @user_router.message(Command('tree'))
# async def is_premium(message: Message):
#     user = await UserDao.find_one_or_none(id=message.from_user.id)
#     if user.is_premium:
#         await message.answer('У тебя премиум')
#     else:
#         await message.answer('У тебя нет премиум')
#
#
# @user_router.message(Command('tray'))
# async def is_premium(message: Message):
#     user = await UserDao.find_one_or_none(id=message.from_user.id)
#     await UserDao.update_premium(user, True)
