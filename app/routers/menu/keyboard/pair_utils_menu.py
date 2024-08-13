from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.i18n import gettext as _

from app.routers.user.pair_router import create_pair, reject_pair, get_pair

pair_keyboard = Router()


def _get_pair_keyboard():
    buttons = [
        [KeyboardButton(text="Мой партнер")],
        [KeyboardButton(text="Создать пару"),
         KeyboardButton(text="Изменить пару")],
        [KeyboardButton(text="Назад в меню")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        one_time_keyboard=True,  # Этот параметр означает, что клавиатура будет показана только один раз
        resize_keyboard=True,
        input_field_placeholder=_("Выберите пункт меню")  # Это текст, который будет показан в поле ввода вверху экрана
    )
    return keyboard


@pair_keyboard.message(F.text.contains("Пара"))
async def start_game(message: types.Message):
    await message.reply("Пункт пар", reply_markup=_get_pair_keyboard())


@pair_keyboard.message(F.text.contains("Создать пару"))
async def add_wish_handler(message: types.Message):
    await create_pair(message)


@pair_keyboard.message(F.text.contains("Мой партнер"))
async def add_wish_handler(message: types.Message):
    await get_pair(message)


@pair_keyboard.message(F.text.contains("Изменить пару"))
async def edit_wish_handler(message: types.Message):
    await reject_pair(message)
