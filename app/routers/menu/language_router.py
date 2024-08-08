from aiogram import types, Router, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from app.config import MEDIA_DIR
from app.routers.menu.menu_router import help_faq
from app.routers.state.states import MenuStateForm
from app.routers.utils import edit_callback_message

language_router = Router()

user_data = {}


@language_router.message(Command("set_language"))
@language_router.message(MenuStateForm.choosing_language)
async def set_language(message: types.Message, state: FSMContext) -> None:
    user_data[message.from_user.id] = 0
    photo_path = MEDIA_DIR / 'image1.jpg'  # Динамическое формирование пути
    await message.answer_photo(
        photo=FSInputFile(photo_path),
        caption="Выберите язык / Select language",
        reply_markup=get_keyboard()
    )
    data = await state.get_data()
    if data.get('from_start', False):
        await state.set_state(MenuStateForm.choosing_type)
    else:
        await state.clear()


def get_keyboard():
    buttons = [
        [types.InlineKeyboardButton(text="Русский", callback_data="l_ru"),
         types.InlineKeyboardButton(text="English", callback_data="l_en")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


@language_router.callback_query(F.data.startswith("l_"))
async def callbacks_language(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]

    if action == "ru":
        await edit_callback_message(callback,
                                    caption="Основной язык русский",
                                    img_path='image3.jpg',
                                    reply_markup=get_keyboard())
    if action == "en":
        await edit_callback_message(callback,
                                    caption="Main language English",
                                    img_path='image3.jpg',
                                    reply_markup=get_keyboard())

    await callback.answer()
    current_state = await state.get_state()
    if current_state == MenuStateForm.choosing_type.state:
        await help_faq(callback.message, state)
