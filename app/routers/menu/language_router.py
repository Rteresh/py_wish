from aiogram import Router, F
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.utils.i18n import I18n, FSMI18nMiddleware

from app.config import DIR
from app.config import MEDIA_DIR
from app.routers.menu.faq_router import help_faq
from app.routers.state.states import MenuStateForm
from app.routers.utils import edit_callback_message

language_router = Router()

user_data = {}

i18n = I18n(path=DIR / 'locales', default_locale='ru', domain='messages')

i18n_middleware = FSMI18nMiddleware(i18n=i18n)


@language_router.message(MenuStateForm.choosing_language)
async def display_language_selection(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает команду установки языка, показывает пользователю выбор языка.

    Args:
        message (types. Message): Сообщение от пользователя.
        state (FSMContext): Состояние конечного автомата.
    """
    user_data[message.from_user.id] = 0
    photo_path = MEDIA_DIR / 'image1.jpg'  # Динамическое формирование пути
    await message.answer_photo(
        photo=FSInputFile(photo_path),
        caption="Выберите язык / Select language",
        reply_markup=_get_language_keyboard()
    )
    data = await state.get_data()
    if data.get('from_start', False):
        await state.set_state(MenuStateForm.choosing_type)
    else:
        await state.clear()


def _get_language_keyboard():
    """
    Создает клавиатуру для выбора языка.

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками выбора языка.
    """
    buttons = [
        [types.InlineKeyboardButton(text="Русский", callback_data="l_ru"),
         types.InlineKeyboardButton(text="English", callback_data="l_en")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


@language_router.callback_query(F.data.startswith("l_"))
async def callbacks_language(callback: types.CallbackQuery, state: FSMContext):
    """
      Обрабатывает выбор языка пользователя из inline-клавиатуры.
      Изменяет язык интерфейса на английский или русский.


      Args:
          callback (types.CallbackQuery): Callback от пользователя.
          state (FSMContext): Состояние конечного автомата.
      """
    action = callback.data.split("_")[1]

    if action == "ru":
        await edit_callback_message(callback,
                                    caption="Основной язык русский",
                                    img_path='image3.jpg',
                                    reply_markup=_get_language_keyboard())

        await i18n_middleware.set_locale(state=state, locale='en')

    if action == "en":
        await edit_callback_message(callback,
                                    caption="Main language English",
                                    img_path='image3.jpg',
                                    reply_markup=_get_language_keyboard())

        await i18n_middleware.set_locale(state=state, locale='en')

    await callback.answer()
    current_state = await state.get_state()
    if current_state == MenuStateForm.choosing_type.state:
        await help_faq(callback.message, state)
