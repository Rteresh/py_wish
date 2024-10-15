from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __


from app.routers.wish.history_router import get_wish_history_owner, get_wish_history_executor

history_keyboard = Router()


def _get_wish_keyboard():
    buttons = [
        [KeyboardButton(text=_("Мои желаний")),
         KeyboardButton(text=_("Я выполнил"))],
        [KeyboardButton(text=_("Назад в меню"))]

    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        one_time_keyboard=True,  # Этот параметр означает, что клавиатура будет показана только один раз
        resize_keyboard=True,
        input_field_placeholder=_("Выберите пункт меню")  # Это текст, который будет показан в поле ввода вверху экрана
    )
    return keyboard


@history_keyboard.message(F.text == __("📜 История"))
async def history_handler(message: types.Message):
    await message.reply(_("Пункт истории"), reply_markup=_get_wish_keyboard())


@history_keyboard.message(F.text == __("Мои желаний"))
async def get_owner_history_handler(message: types.Message):
    await get_wish_history_owner(message)


@history_keyboard.message(F.text == __("Я выполнил"))
async def get_executor_history_handler(message: types.Message):
    await get_wish_history_executor(message)
