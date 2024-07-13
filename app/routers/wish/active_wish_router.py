from asyncio import sleep
from datetime import datetime

from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.dao.user.pair_dao import PairDao
from app.dao.user.user_dao import UserDao
from app.dao.wish.active_wish_dao import ActiveDao
from app.models.user.models import User

active_router = Router()


@active_router.message(Command('doit'))
async def create_active_wish(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    if await _check_active_wish(user):
        await get_active(user, message)
    else:
        if await PairDao.get_my_partner(user):
            await ActiveDao.create_active_wish(user)
            await get_active(user, message)
        else:
            await message.answer('У вас еще нет партнера!')


async def _check_active_wish(user) -> bool:
    active_wish = await ActiveDao.get_active_wish_by_executor(user)
    if not active_wish:
        return False
    return True


async def get_active(user: User, message: Message):
    active_wish = await ActiveDao.get_active_wish_by_executor(user)
    if not active_wish:
        await message.answer(_('У вас еще нет активного желания'))
        return
    await message.answer(
        _('Ваша желание: {title}\n').format(title=active_wish.title),
        _('Срок на выполнение:{expired_at}\n').format(expired_at=active_wish.expired_at)
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
        await message.answer(_('У вас еще нет активного желания'))
        return

    days, hours, minutes = await _get_time_until_expiration(active_wish.expired_at)
    await message.answer(
        _('Ваше желание: {title}\n').format(tittle=active_wish.title),
        _('Вам осталось {days} дней {hours} часов {minutes} минут до истечения срока.\n').format(days=days, hours=hours,
                                                                                                 minutes=minutes)
    )


async def _get_time_until_expiration(expiration_date: datetime):
    now = datetime.now()
    # Разница между датой истечения срока и текущим временем
    time_delta = expiration_date - now
    # Преобразование разницы в дни, часы и минуты
    days = time_delta.days
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return days, hours, minutes


@active_router.message(Command('done'))
async def send_confirmation_request(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    if not await _check_active_wish(user):
        await message.answer(_('У вас еще нет активного желания'))
        return
    wish = await ActiveDao.get_active_wish_by_executor(user)
    partner = await PairDao.get_my_partner(user)
    buttons = [
        InlineKeyboardButton(text=_("Подтвердить"), callback_data="confirm", cache_time=0),
        InlineKeyboardButton(text=_("Отклонить"), callback_data="reject", cache_time=0)
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    await message.bot.send_message(partner.id,
                                   _("Пожалуйста, подтвердите выполнение желания: {title}\n").format(
                                       tittle=wish.title), _("Выполнил: {username}.").format(username=user.username),
                                   reply_markup=keyboard)


@active_router.callback_query(lambda c: c.data in ['confirm', 'reject'])
async def process_callback(callback_query: CallbackQuery):
    action = callback_query.data
    user = await UserDao.find_one_or_none(id=callback_query.from_user.id)
    partner = await PairDao.get_my_partner(user)
    wish = await ActiveDao.get_my_active_wish(partner)
    if action == "confirm":
        if wish:
            response_text = _("Вы подтвердили действие.")
            await ActiveDao.confirm_active_wish(partner)
            await _send_accept_request(callback_query.bot, partner, user)
        else:
            response_text = _("Запрос был уже выполнен")
    else:
        if wish:
            response_text = _("Вы отклонили действие.")
            await ActiveDao.reject_active_wish(partner)
        else:
            response_text = _("Запрос был уже выполнен")

    await callback_query.answer()  # Уведомление Telegram, что callback получен
    # Обновляем сообщение, удаляя клавиатуру
    await callback_query.bot.edit_message_text(chat_id=user.id,
                                               text=response_text,
                                               message_id=callback_query.message.message_id,
                                               reply_markup=None)


@active_router.message(Command('test1'))
async def get_test(message: Message):
    active_wishes = await ActiveDao.get_all_unfulfilled_wish()
    for active_wish in active_wishes:
        owner = await UserDao.find_one_or_none(id=active_wish.owner_id)
        executor = await UserDao.find_one_or_none(id=active_wish.executor_id)
        await message.answer(_("Ваше желание {title} не выполнено,\n").format(tittle=active_wish.title),
                             _(" партнером:{username}.").format(executor=executor.username),
                             )
        await sleep(10)
        await message.answer(_("Ваше желание {title} не выполнено,\n").format(tittle=active_wish.title),
                             _(" партнером:{username}.").format(username=executor.username),
                             )


async def _send_accept_request(bot, partner, user):
    await bot.send_message(partner.id,
                           _(" 'Спасибо большое, что выполнил мое желание' "),
                           _("с любовью от партнера {username}.\n").format(username=user.username))
