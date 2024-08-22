from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.i18n import gettext as _

from app.dao.user.user_dao import UserDao
from app.dao.wish.active_wish_dao import ActiveDao

main_keyboard = Router()


def get_main_keyboard(active_wish=False):
    if active_wish:
        start_button = [KeyboardButton(text=_("🎯 Активное желание"))]
    else:
        start_button = [KeyboardButton(text="🎲 Начать игру")]

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
        one_time_keyboard=False,  # Этот параметр означает, что клавиатура будет показана только один раз
        resize_keyboard=True,
        input_field_placeholder=_("Выберите пункт меню")
    )
    return keyboard


@main_keyboard.message(F.text.contains("Назад в меню"))
async def step_back_utils(message: types.Message):
    await message.answer("Главное меню", reply_markup=get_main_keyboard(await _flag(message)))


@main_keyboard.message(Command("menu"))
async def main_menu(message: types.Message):
    await message.answer("Главное меню", reply_markup=get_main_keyboard(await _flag(message)))


@main_keyboard.callback_query(F.data.startswith("menu_back"))
async def inline_menu_back(callback: types.CallbackQuery):
    await callback.message.edit_text(text=_('Назад в меню'), reply_markup=None)


async def update_main_keyboard(message: types.Message):
    await message.answer(_('Удачи в выполнении'), reply_markup=get_main_keyboard(await _flag(message)))


async def _flag(message: types.Message) -> bool:
    user = await UserDao.find_by_id(message.from_user.id)
    return await ActiveDao.check_active_wish(user)


@main_keyboard.message(F.text.contains('Режим 18+'))
async def premium_main(message: types.Message):
    await message.answer("Пока недоступно/скоро...", reply_markup=get_main_keyboard(await _flag(message)))

# inline menu back

# def _get_inline_main_keyboard():
#     buttons = [
#         [InlineKeyboardButton(text=_("Назад в меню"), callback_data="menu_back")],
#     ]
#     keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
#
#     return keyboard


# async def inline_main_menu(message: types.Message):
#     await message.answer(text=_('Назад в меню'), reply_markup=_get_inline_main_keyboard())
