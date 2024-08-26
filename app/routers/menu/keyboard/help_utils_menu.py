from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from app.routers.menu.faq_router import help_faq

help_keyboard = Router()


def _get_help_keyboard():
    buttons = [
        [KeyboardButton(text=_("Часто задаваемые вопросы FAQ")),
         KeyboardButton(text=_("Связаться с нами"))],
        [KeyboardButton(text=_("Назад в меню"))]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        one_time_keyboard=True,  # Этот параметр означает, что клавиатура будет показана только один раз
        resize_keyboard=True,
        input_field_placeholder=_("Выберите пункт меню")  # Это текст, который будет показан в поле ввода вверху экран
    )
    return keyboard


@help_keyboard.message(F.text == __("Часто задаваемые вопросы FAQ"))
async def faq_menu(message: types.Message, state: FSMContext):
    await help_faq(message, state)


@help_keyboard.message(F.text == (__("❓Помощь")))
async def help_utils(message: types.Message):
    await message.reply("Пункт помощи", reply_markup=_get_help_keyboard())
