from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.i18n import gettext as _

from app.routers.menu.menu_router import help_faq

help_keyboard = Router()


def get_help_keyboard():
    buttons = [
        [KeyboardButton(text="Часто задаваемые вопросы FAQ"),
         KeyboardButton(text="Связаться с нами")],
        [KeyboardButton(text="Назад в меню")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        one_time_keyboard=True,  # Этот параметр означает, что клавиатура будет показана только один раз
        resize_keyboard=True,
        input_field_placeholder=_("Выберите пункт меню")  # Это текст, который будет показан в поле ввода вверху экран
    )
    return keyboard


@help_keyboard.message(F.text.contains("Часто задаваемые вопросы FAQ"))
async def start_game(message: types.Message, state: FSMContext):
    await help_faq(message, state)


@help_keyboard.message(F.text.contains("Помощь"))
async def help_utils(message: types.Message):
    await message.reply("Пункт помощи", reply_markup=get_help_keyboard())
