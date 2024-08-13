from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from app.dao.user.pair_dao import PairDao
from app.dao.user.user_dao import UserDao
from app.models.user.models import PairRequest

pair_router = Router()


@pair_router.message(Command('create_pair'))
async def create_pair(message: Message):
    """
    Обработчик команды /create_pair. Создает запрос на пару для пользователя.

    :param message: Сообщение от пользователя.
    """
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    if not user:
        await message.answer(_('Пользователь не найден.'))
        return

    request = await PairDao.create_pair_request(user)
    await message.answer(_('Запрос на пару создан: {request}').format(request=request))


@pair_router.message(Command('get_pair'))
async def get_pair(message: Message):
    """
    Обработчик команды /get_pair. Отправляет пользователю информацию о его партнере.

    :param message: Сообщение от пользователя.
    """
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    if not user:
        await message.answer(_('Пользователь не найден.'))
        return

    partner = await PairDao.get_my_partner(user)
    if not partner:
        await message.answer(_('У вас еще нет партнера!'))
    else:
        await message.answer(_('Ваш партнер: {partner}').format(partner=partner.username))


@pair_router.message(Command('reject_pair'))
async def reject_pair(message: Message):
    """
    Обработчик команды /reject_pair. Удаляет текущую пару пользователя.

    :param message: Сообщение от пользователя.
    """
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    if not user:
        await message.answer(_('Пользователь не найден.'))
        return

    pair = await PairDao.get_my_pair(user)
    if not pair:
        await message.answer(_('У вас еще нет пары!'))
        return

    await PairDao.delete_my_pair(user)
    await message.answer(_('Вы больше не являетесь партнерами!'))


async def delete_pair_request(request: PairRequest) -> None:
    """
    Удаляет запрос на пару.

    :param request: Объект запроса на пару.
    """
    await PairDao.delete_pair_request(request)
