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
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    request = await PairDao.create_pair_request(user)
    await message.answer(
        _('Запрос создан {request}').format(request=request)
    )


@pair_router.message(Command('get_pair'))
async def get_pair(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    partner = await PairDao.get_my_partner(user)
    if not partner:
        await message.answer(
            _('У вас еще нет партнера!')
        )
    else:
        await message.answer(
            _('Ваш партнер:{partner}').format(partner=partner.username)
        )


@pair_router.message(Command('reject_pair'))
async def reject_pair(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    pair = await PairDao.get_my_pair(user)
    if not pair:
        await message.answer(
            _('У вас еще нет партнера!')
        )
    else:
        await PairDao.delete_my_pair(user)
        await message.answer(
            _('Вы больше не являетесь партнерами!')
        )


# async def schedule_delete_timeout_pair_requests() -> None:
#     pairs_requests = await PairDao.find_all(PairRequest,
#                                             PairRequest.)


async def delete_pair_request(request: PairRequest) -> None:
    await PairDao.delete_pair_request(request)
