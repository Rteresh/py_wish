from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.utils.i18n import gettext as _

from app.config import MEDIA_DIR
from app.routers.menu.keyboard.main_keyboard_utils_menu import main_menu
from app.routers.state.states import MenuStateForm
from app.routers.utils import edit_callback_message
from app.text.menu.faq import get_faq_one, get_faq_two
from app.text.menu.rules import get_rules

menu_router = Router()

user_data = {}


# -------------------------------
# Это вариант с фабрикой колбэков
@menu_router.message(MenuStateForm.choosing_type)
async def help_faq(message: types.Message, state: FSMContext) -> None:
    user_data[message.from_user.id] = 0
    photo_path = MEDIA_DIR / 'image1.jpg'  # Динамическое формирование пути
    await message.answer_photo(
        photo=FSInputFile(photo_path),
        caption=_("Нажмите на одну из кнопок, чтобы бот отправил число от 1 до 10"),
        reply_markup=get_keyboard()
    )
    await state.set_state(MenuStateForm.choosing_type)
    await state.clear()


def get_keyboard(show_rules=True, show_faq=True, show_settings=True, b_next=False, b_back=False):
    buttons = []

    if b_back:
        buttons.append([types.InlineKeyboardButton(text=_("Назад"), callback_data="h_back")])

    if b_next:
        buttons.append([types.InlineKeyboardButton(text=_("Дальше"), callback_data="h_next")])

    if show_rules:
        buttons.append([types.InlineKeyboardButton(text=_("Правила пользования 📖"), callback_data="h_rules")])

    if show_faq:
        buttons.append([types.InlineKeyboardButton(text=_("FAQ \ud83e\udde0"), callback_data="h_faq")])

    buttons.append([types.InlineKeyboardButton(text=_("Главное меню"), callback_data="h_menu")])

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


# TODO УБРАТЬ
@menu_router.callback_query(F.data.startswith("h_"))
async def callbacks_num(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]

    if action == "faq":
        await edit_callback_message(callback,
                                    caption=await get_faq_one(),
                                    img_path='image1.jpg',
                                    reply_markup=get_keyboard(show_faq=False, b_next=True))
    elif action == "rules":
        await edit_callback_message(callback,
                                    caption=await get_rules(),
                                    img_path='image2.jpg',
                                    reply_markup=get_keyboard(show_rules=False))
    elif action == "next":
        await edit_callback_message(callback,
                                    caption=await get_faq_two(),
                                    img_path='image1.jpg',
                                    reply_markup=get_keyboard(show_faq=False, b_back=True))
    elif action == "back":
        await edit_callback_message(callback,
                                    caption=await get_faq_one(),
                                    img_path='image1.jpg',
                                    reply_markup=get_keyboard(show_faq=False, b_next=True))
    elif action == "menu":
        await main_menu(callback.message)
    await state.clear()

# ----------
# Это вариант с фабрикой колбэков
