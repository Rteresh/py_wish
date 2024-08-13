from datetime import datetime

from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.crypto.encryption_manager import decrypt as d
from app.dao.user.pair_dao import PairDao
from app.dao.user.user_dao import UserDao
from app.dao.wish.active_wish_dao import ActiveDao
from app.dao.wish.wish_dao import WishDao
from app.models.user.models import User
from app.models.wishes.models import ActiveWish
from app.routers.user.pair_router import create_pair
from app.routers.utils import accept_wish, reject_wish

# Инициализация роутера для обработки команд, связанных с активными желаниями
active_router = Router()


async def _get_active_wish_for_user(user: User) -> ActiveWish:
    """
    Получает активное желание для пользователя из базы данных.

    :param user: Объект пользователя, для которого ищется активное желание.
    :return: Объект ActiveWish, если активное желание существует, или None.
    """
    return await ActiveDao.get_active_wish_by_executor(user)


async def _get_partner_for_user(user: User) -> User:
    """
    Получает партнера для пользователя из базы данных.

    :param user: Объект пользователя, для которого ищется партнер.
    :return: Объект User, представляющий партнера, или None.
    """
    return await PairDao.get_my_partner(user)


async def create_active_wish(message: Message) -> None:
    """
    СОЗДАЕТ ЗАПИСЬ АКТИВНОГО ЖЕЛАНИЯ ДЛЯ ПОЛЬЗОВАТЕЛЯ
    :param message: Объект Message, представляющий сообщение от пользователя.
    """
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    if not user:
        await message.answer(_('Пользователь не найден'))
        return

    active_wish = await _get_active_wish_for_user(user)
    if active_wish:
        await message.answer(await _get_active_time(active_wish))
    else:
        partner = await _get_partner_for_user(user)
        if partner:
            wishes = await WishDao.get_all_wish_by_user(partner)
            if not bool(wishes):
                await message.answer(_('У партнера пока нет желаний!'))
                return
            else:
                await ActiveDao.create_active_wish(user)
                await message.answer(await _get_active_time(await ActiveDao.get_active_wish_by_executor(user)
                                                            ))
        else:
            await message.answer(_('У вас еще нет партнера!'))
            await create_pair(message)


async def get_active_time(message: Message) -> None:
    """
    Отправляет пользователю информацию о времени, оставшемся до истечения активного желания.

    :param message: Объект Message, представляющий сообщение от пользователя.
    """
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    if not user:
        await message.answer(_('Пользователь не найден'))
        return

    active_wish = await _get_active_wish_for_user(user)
    if not active_wish:
        await message.answer(_('У вас еще нет активного желания'))
        return

    await message.answer(await _get_active_time(active_wish))


async def _get_active_time(active_wish: ActiveWish) -> str:
    """
    Формирует текстовую информацию о времени, оставшемся до истечения активного желания.

    :param active_wish: Объект ActiveWish, представляющий активное желание.
    :return: Строка с информацией о желании и времени до его истечения.
    """
    days, hours, minutes = await _get_time_until_expiration(active_wish.expired_at)

    if days < 0:
        text = _("Время на исполнение желания: {title} истекло").format(
            title=d(active_wish.title))
    else:
        text = _("Ваше желание: {title}\n"
                 "Срок на выполнение: {expired_at}\n"
                 "Осталось {days} дней {hours} часов {minutes} минут до истечения срока.\n").format(
            title=d(active_wish.title),
            expired_at=active_wish.expired_at,
            days=days,
            hours=hours,
            minutes=minutes)
    return text


async def _get_time_until_expiration(expiration_date: datetime) -> tuple[int, int, int]:
    """
    Вычисляет и возвращает время до истечения срока желания в днях, часах и минутах.

    :param expiration_date: Дата и время истечения срока желания.
    :return: Кортеж, содержащий количество дней, часов и минут до истечения срока.
    """
    now = datetime.now()
    time_delta = expiration_date - now
    days = time_delta.days
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return days, hours, minutes


async def send_confirmation_request(message: Message) -> None:
    """
    Отправляет запрос на подтверждение выполнения желания партнеру пользователя.

    :param message: Объект Message, представляющий сообщение от пользователя.
    """
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    if not user:
        await message.answer(_('Пользователь не найден'))
        return

    active_wish = await _get_active_wish_for_user(user)
    if not active_wish:
        await message.answer(_('У вас еще нет активного желания'))
        return

    partner = await _get_partner_for_user(user)
    if not partner:
        await message.answer(_('Партнер не найден'))
        return

    buttons = [
        InlineKeyboardButton(text=_("Подтвердить"), callback_data="confirm"),
        InlineKeyboardButton(text=_("Отклонить"), callback_data="reject")
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    await message.bot.send_message(
        partner.id,
        _("Пожалуйста, подтвердите выполнение желания: {title}\n").format(title=d(active_wish.title)) +
        _("Выполнил: {username}.").format(username=user.username),
        reply_markup=keyboard
    )
    await message.answer('Запрос на подтверждение отправлен вашему партнеру!')


@active_router.callback_query(lambda c: c.data in ['confirm', 'reject'])
async def process_callback(callback_query: CallbackQuery) -> None:
    """
    Обработчик callback-запросов для подтверждения или отклонения выполнения желания.

    :param callback_query: Объект CallbackQuery, представляющий запрос от пользователя.
    """
    action = callback_query.data
    user = await UserDao.find_one_or_none(id=callback_query.from_user.id)
    if not user:
        await callback_query.answer(_('Пользователь не найден'))
        return

    partner = await _get_partner_for_user(user)
    active_wish = await ActiveDao.get_active_wish_by_executor(partner)

    if not active_wish:
        response_text = _("Запрос уже был выполнен")
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


async def _send_accept_request(bot, partner: User, user: User) -> None:
    """
    Отправляет пользователю сообщение о том, что его желание было принято его партнером.

    :param bot: Объект бота для отправки сообщений.
    :param partner: Объект User, представляющий партнера.
    :param user: Объект User, представляющий пользователя.
    """
    await bot.send_message(
        partner.id,
        _("Спасибо большое, что выполнил мое желание") +
        _("с любовью от партнера {username}.\n").format(username=user.username)
    )


async def change_active_wish(message: Message):
    await message.answer(_("Функция сейчас не доступна"))
