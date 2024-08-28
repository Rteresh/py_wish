from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.i18n import gettext as _

from app.config import settings
from app.dao.promo.promo_dao import PromoDao
from app.dao.user.user_dao import UserDao
from app.models.user.models import User

# Инициализация роутера для обработки команд, связанных с активными желаниями
promo_router = Router()


class PromoStates(StatesGroup):
    """
    Состояния для работы с промокодами.
    """
    enter_promo_code = State()  # Ввод промокода
    promo_code_accepted = State()  # Промокод принят
    promo_code_rejected = State()  # Промокод отклонен


async def _enter_promo_code(user: User, text: str) -> str:
    """
    Обрабатывает введенный пользователем промокод.

    Args:
        user: Объект пользователя.
        text: Текст промокода.

    Returns:
        Строка с информацией о результатах обработки промокода.
    """
    text = text.lstrip('/').upper()  # Удаляем начальный слэш, если он есть
    promo = await PromoDao.get_promo_by_code(text)
    if len(text) > settings.MAX_WISH_LENGTH:
        return _('Текст должен быть не более 128 символов!')
    if promo and promo.is_valid():
        await UserDao.update_premium(
            user=user,
            is_premium=True,
            time=promo.premium_duration)
        await PromoDao.set_finished(promo)
        return _('Промокод активирован! Длительность премиум аккаунта увеличено на: {duration} месяцев.').format(
            duration=promo.premium_duration
        )
    return _('Промокод не найден или недействителен!')


async def enter_promo_code(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /promo. Начинает процесс ввода промокода.

    :param message: Сообщение от пользователя.
    :param state: Состояние машины состояний FSMContext.
    """
    await state.set_state(PromoStates.enter_promo_code)
    await message.answer(_('Введите промокод:'), reply_markup=ReplyKeyboardRemove())


@promo_router.message(PromoStates.enter_promo_code)
async def process_promo_code(message: Message, state: FSMContext) -> None:
    """
    Обработчик ввода промокода.

    :param message: Сообщение от пользователя.
    :param state: Состояние машины состояний FSMContext.
    """

    await state.update_data(promo_code=message.text)
    await state.set_state(PromoStates.promo_code_accepted)
    user = await UserDao.find_by_id(message.from_user.id)
    await message.answer(text=await _enter_promo_code(user, message.text))
    await state.clear()
