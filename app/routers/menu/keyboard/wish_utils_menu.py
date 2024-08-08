from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.i18n import gettext as _

from app.routers.menu.keyboard.main_keyboard_utils_menu import inline_main_menu
from app.routers.wish.wish_routers import get_all_wishes, add_nwish, edit_wishes

wish_keyboard = Router()


def _get_wish_keyboard():
    buttons = [
        [KeyboardButton(text="Мои желания")],
        [KeyboardButton(text="Добавить желание"),
         KeyboardButton(text="Изменить желания")],
        [KeyboardButton(text="Назад в меню")],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        one_time_keyboard=True,  # Этот параметр означает, что клавиатура будет показана только один раз
        resize_keyboard=True,
        input_field_placeholder=_("Выберите пункт меню")  # Это текст, который будет показан в поле ввода вверху экрана
    )
    return keyboard


@wish_keyboard.message(F.text.contains("Желания"))
async def wish_handler(message: types.Message):
    await message.reply("Пункт желания", reply_markup=_get_wish_keyboard())


@wish_keyboard.message(F.text.contains("Мои желания"))
async def add_wish_handler(message: types.Message):
    await get_all_wishes(message)
    await inline_main_menu(message)


@wish_keyboard.message(F.text.contains("Добавить желание"))
async def add_wish_handler(message: types.Message, state: FSMContext):
    await add_nwish(message, state)
    # TODO: надо после добавления желания
    # await inline_main_menu(message)


@wish_keyboard.message(F.text.contains("Изменить желания"))
async def edit_wish_handler(message: types.Message, state: FSMContext):
    # Запускаем процесс редактирования желаний
    await edit_wishes(message, state)
    # TODO: надо после изменения желания
    # await inline_main_menu(message)
