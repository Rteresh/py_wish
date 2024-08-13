from aiogram import Router, types, F
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.i18n import gettext as _

from app.routers.menu.keyboard.main_keyboard_utils_menu import main_menu, update_main_keyboard
from app.routers.wish.active_wish_router import create_active_wish, send_confirmation_request, get_active_time, \
    change_active_wish

start_keyboard = Router()


@start_keyboard.message(F.text.contains("Начать игру"))
async def start_game_handler(message: types.Message):
    await create_active_wish(message)
    await update_main_keyboard(message)


@start_keyboard.message(F.text.contains("Активное желание"))
async def active_wish_handler(message: types.Message):
    await message.answer("Активное желание", reply_markup=_get_active_keyboard())


def _get_active_keyboard():
    buttons = [
        [KeyboardButton(text="Сообщить о выполнении желания")],
        [KeyboardButton(text="Мое активное желание"),
         KeyboardButton(text="Сменить активное желание")],
        [KeyboardButton(text="Назад в меню")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        one_time_keyboard=True,  # Этот параметр означает, что клавиатура будет показана только один раз
        resize_keyboard=True,
        input_field_placeholder=_("Выберите пункт меню")  # Это текст, который будет показан в поле ввода вверху экрана
    )
    return keyboard


@start_keyboard.message(F.text.contains("Сообщить о выполнении желания"))
async def add_wish_handler(message: types.Message):
    await send_confirmation_request(message)


@start_keyboard.message(F.text.contains("Мое активное желание"))
async def add_wish_handler(message: types.Message):
    await get_active_time(message)


@start_keyboard.message(F.text.contains("Сообщить о выполнении желания"))
async def add_wish_handler(message: types.Message):
    await change_active_wish(message)
