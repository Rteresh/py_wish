from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _

from app.dao.user.user_dao import UserDao
from app.dao.wish.active_wish_dao import ActiveDao

main_keyboard = Router()


def get_main_keyboard(active_wish=True):
    if not active_wish:
        start_button = [KeyboardButton(text="🎲 Начать игру")]
    else:
        start_button = [KeyboardButton(text="Закончить игру"), KeyboardButton(text="Ура игру")]

    buttons = [
        start_button,
        [
            KeyboardButton(text="🌠 Желания"),
            KeyboardButton(text="📜 История"),
            KeyboardButton(text="💑 Пара")
        ],
        [KeyboardButton(text="🔞 Режим 18+")],
        [
            KeyboardButton(text="❓ Помощь"),
            KeyboardButton(text="⚙️ Настройки")
        ],
    ]

    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        one_time_keyboard=True,  # Этот параметр означает, что клавиатура будет показана только один раз
        resize_keyboard=True,
        input_field_placeholder=_("Выберите пункт меню")  # Это текст, который будет показан в поле ввода вверху экрана
    )
    return keyboard


@main_keyboard.message(F.text.contains("Назад в меню"))
async def step_back_utils(message: types.Message):
    await message.answer("Главное меню", reply_markup=get_main_keyboard(
        await ActiveDao.check_active_wish(await UserDao.find_by_id(message.from_user.id))
    ))


@main_keyboard.message(Command("menu"))
async def command_rrr(message: types.Message):
    # await message.answer("Главное меню", reply_markup=get_main_keyboard(False))
    await message.answer("Главное меню", reply_markup=get_main_keyboard(
        await ActiveDao.check_active_wish(await UserDao.find_by_id(message.from_user.id))
    ))


def _get_inline_main_keyboard():
    buttons = [
        [InlineKeyboardButton(text=_("Назад в меню"), callback_data="menu_back")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def inline_main_menu(message: types.Message):
    await message.answer(text=_('Назад в меню'), reply_markup=_get_inline_main_keyboard())


@main_keyboard.callback_query(F.data.startswith("menu_back"))
async def inline_menu_back(callback: types.CallbackQuery):
    await callback.message.edit_text(text=_('Назад в меню'), reply_markup=None)
    await command_rrr(callback.message)
