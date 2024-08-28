from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from app.routers.menu.language_router import display_language_selection
from app.routers.promo.promo_routers import enter_promo_code

settings_keyboard = Router()


def _get_settings_keyboard():
    """
    Создает клавиатуру с настройками для пользователя.

    Returns:
        ReplyKeyboardMarkup: Клавиатура с кнопками настроек.
    """
    buttons = [
        [KeyboardButton(text=_("Промокод")),
         KeyboardButton(text=_("Язык"))],
        [KeyboardButton(text=_("Назад в меню"))]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        one_time_keyboard=True,  # Этот параметр означает, что клавиатура будет показана только один раз
        resize_keyboard=True,
        input_field_placeholder=_("Выберите пункт меню")  # Это текст, который будет показан в поле ввода вверху экран
    )
    return keyboard


@settings_keyboard.message(F.text == __("Язык"))
async def change_language(message: types.Message, state: FSMContext):
    """
    Обрабатывает команду изменения языка из меню настроек.

    Args:
        message (types. Message): Сообщение от пользователя.
        state (FSMContext): Состояние конечного автомата.
    """
    await display_language_selection(message, state)


@settings_keyboard.message(F.text == __("⚙️Настройки"))
async def settings_utils(message: types.Message):
    """
    Обрабатывает команду открытия настроек из меню.

    Args:
        message (types. Message): Сообщение от пользователя.
    """
    await message.reply(_("Настройки"), reply_markup=_get_settings_keyboard())


@settings_keyboard.message(F.text == __("Промокод"))
async def promo_code(message: types.Message, state: FSMContext):
    """
    Обрабатывает команду открытия промокода из меню.

    Args:
        message (types. Message): Сообщение от пользователя.
        state: Состояние конечного автомата
    """
    await enter_promo_code(message, state)
