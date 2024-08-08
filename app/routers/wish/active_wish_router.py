from datetime import datetime

from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.crypto.encryption_manager import _decr
from app.dao.user.pair_dao import PairDao  # DAO для работы с данными пар
from app.dao.user.user_dao import UserDao  # DAO для работы с данными пользователей
from app.dao.wish.active_wish_dao import ActiveDao  # DAO для работы с активными желаниями
from app.dao.wish.history_dao import HistoryDao
from app.models.user.models import User
from app.models.wishes.models import ActiveWish
from app.routers.user.pair_router import create_pair
from app.routers.utils import accept_wish, reject_wish

active_router = Router()  # Создание роутера для обработки команд


# Убрано лишнее дублирование запросов к базе данных и оптимизированы функции для упрощения кода


@active_router.message(Command('doit'))
async def create_active_wish(message: Message):
    """
    Обработчик команды /doit. Создает активное желание для пользователя или сообщает, если его нет.

    :param message: Сообщение от пользователя.
    """
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    active_wish = await ActiveDao.get_active_wish_by_executor(user)
    if active_wish:
        await message.answer(await _get_active_time(active_wish))
    else:
        partner = await PairDao.get_my_partner(user)
        if partner:
            active = await ActiveDao.create_active_wish(user)
            if not active:
                await message.answer(_('У партнера пока нету желаний!'))
        else:
            await message.answer(_('У вас еще нет партнера!'))
            await create_pair(message)


async def _check_active_wish(user: User) -> bool:
    """
    Проверяет наличие активного желания у пользователя.

    :param user: Объект пользователя.
    :return: True, если есть активное желание, иначе False.
    """
    active_wish = await ActiveDao.get_active_wish_by_executor(user)
    return bool(active_wish)


@active_router.message(Command('get_time'))
async def get_active_time(message: Message):
    """
    Обработчик команды /get_time. Отправляет пользователю информацию о времени до истечения активного желания.

    :param message: Сообщение от пользователя.
    """
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    active_wish = await ActiveDao.get_active_wish_by_executor(user)
    if not active_wish:
        await message.answer(_('У вас еще нет активного желания'))
        return
    await message.answer(await _get_active_time(active_wish))


async def _get_active_time(active_wish: ActiveWish) -> str:
    """
    Возвращает текстовую информацию о времени до истечения активного желания.

    :param active_wish: Объект активного желания.
    :return: Текстовая информация о желании и времени до его истечения.
    """
    days, hours, minutes = await _get_time_until_expiration(active_wish.expired_at)

    if days < 0:
        text = _("Время на исполнение желания: {title} истекло").format(
            title=_decr(active_wish.title))

    else:
        text = _("Ваше желание: {title}\n"
                 "Срок на выполнение: {expired_at}\n"
                 "Осталось {days} дней {hours} часов {minutes} минут до истечения срока.\n").format(
            title=_decr(active_wish.title),
            expired_at=active_wish.expired_at,
            days=days,
            hours=hours,
            minutes=minutes)
    return text


async def _get_time_until_expiration(expiration_date: datetime) -> tuple:
    """
    Вычисляет время до истечения срока желания.

    :param expiration_date: Дата истечения срока.
    :return: Кортеж (days, hours, minutes) до истечения срока.
    """
    now = datetime.now()
    time_delta = expiration_date - now
    days = time_delta.days
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return days, hours, minutes


@active_router.message(Command('done'))
async def send_confirmation_request(message: Message):
    """
    Обработчик команды /done. Отправляет запрос на подтверждение выполнения желания партнеру.

    :param message: Сообщение от пользователя.
    """
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    if not await _check_active_wish(user):
        await message.answer(_('У вас еще нет активного желания'))
        return
    active_wish = await ActiveDao.get_active_wish_by_executor(user)
    partner = await PairDao.get_my_partner(user)
    buttons = [
        InlineKeyboardButton(text=_("Подтвердить"), callback_data="confirm"),
        InlineKeyboardButton(text=_("Отклонить"), callback_data="reject")
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    await message.bot.send_message(
        partner.id,
        _("Пожалуйста, подтвердите выполнение желания: {title}\n").format(title=_decr(active_wish.title)) +
        _("Выполнил: {username}.").format(username=user.username),
        reply_markup=keyboard
    )


@active_router.callback_query(lambda c: c.data in ['confirm', 'reject'])
async def process_callback(callback_query: CallbackQuery):
    """
    Обработчик callback-запросов для подтверждения или отклонения выполнения желания.

    :param callback_query: Callback-запрос от пользователя.
    """

    action = callback_query.data
    user = await UserDao.find_one_or_none(id=callback_query.from_user.id)
    partner = await PairDao.get_my_partner(user)
    active_wish = await ActiveDao.get_my_active_wish(partner)

    if not active_wish:
        response_text = _("Запрос был уже выполнен")
    elif action == "confirm":
        response_text = _("Вы подтвердили действие.")
        await accept_wish(active_wish, partner)
        await _send_accept_request(callback_query.bot, partner, user)
    else:
        response_text = _("Вы отклонили действие.")
        await reject_wish(active_wish, partner)

    await callback_query.answer()
    await callback_query.bot.edit_message_text(
        chat_id=user.id,
        text=response_text,
        message_id=callback_query.message.message_id,
        reply_markup=None
    )

    await HistoryDao.create_wish_history(active_wish)


async def _send_accept_request(bot, partner: User, user: User):
    """
    Отправляет пользователю сообщение о принятии выполнения желания его партнером.

    :param bot: Объект бота.
    :param partner: Объект пользователя (партнер).
    :param user: Объект пользователя.
    """
    await bot.send_message(
        partner.id,
        _("Спасибо большое, что выполнил мое желание") +
        _("с любовью от партнера {username}.\n").format(username=user.username)
    )
