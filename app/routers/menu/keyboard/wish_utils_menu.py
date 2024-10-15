from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from app.routers.wish.wish_router import get_all_wishes, add_wish, edit_wishes

wish_keyboard = Router()


def _get_wish_keyboard():
    buttons = [
        [KeyboardButton(text=_("Мои желания"))],
        [KeyboardButton(text=_("Добавить желание")),
         KeyboardButton(text=_("Изменить желания"))],
        [KeyboardButton(text=_("Назад в меню"))],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        one_time_keyboard=True,  # Этот параметр означает, что клавиатура будет показана только один раз
        resize_keyboard=True,
        input_field_placeholder=_("Выберите пункт меню")  # Это текст, который будет показан в поле ввода вверху экрана
    )
    return keyboard


@wish_keyboard.message(F.text == __("🌠 Желания"))
async def wish_handler(message: types.Message):
    await message.answer(_("🌠 Пункт желаний"), reply_markup=_get_wish_keyboard())


@wish_keyboard.message(F.text == __("Мои желания"))
async def add_wish_handler(message: types.Message):
    await get_all_wishes(message)


@wish_keyboard.message(F.text == __("Добавить желание"))
async def add_wish_handler(message: types.Message, state: FSMContext):
    await add_wish(message, state)


@wish_keyboard.message(F.text == __("Изменить желания"))
async def edit_wish_handler(message: types.Message, state: FSMContext):
    await edit_wishes(message, state)
