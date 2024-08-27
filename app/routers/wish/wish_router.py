import html

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _

from app.config import settings
from app.crypto.encryption_manager import decrypt as d
from app.dao.user.user_dao import UserDao
from app.dao.wish.wish_dao import WishDao

wish_router = Router()


class AddWish(StatesGroup):
    """
    Состояния для добавления и редактирования желаний.
    """
    name = State()  # Ввод текста нового желания
    next_wish = State()  # Запрос на добавление еще одного желания
    confirm_wish = State()  # Подтверждение добавления желания
    edit_text = State()  # Ввод нового текста для редактирования желания
    update_wish = State()  # Обновление существующего желания
    edit_choice = State()  # Выбор желания для редактирования


async def _add_wish(message: Message, text: str) -> bool:
    """
    Добавляет новое желание пользователя в базу данных.

    :param message: Сообщение от пользователя.
    :param text: Текст желания.
    :return: True, если желание добавлено успешно, иначе False.
    """
    text = text.lstrip('/')  # Удаляем начальный слэш, если он есть
    if len(text) > settings.MAX_WISH_LENGTH:
        return False
    user = await UserDao.find_by_id(message.from_user.id)
    await WishDao.create_wish(text=text, user=user)
    return True


async def check_wish_limit(user) -> bool:
    """
    Проверяет, достиг ли пользователь лимита желаний.

    :param user: Объект пользователя.
    :return: True, если пользователь не достиг лимита, иначе False.
    """
    wishes = await WishDao.get_all_wish_by_user(user)
    limit = settings.COUNT_WISH_PREMIUM if user.is_premium else settings.COUNT_WISH
    return len(wishes) < limit


@wish_router.message(Command('get_all_wishes'))
async def get_all_wishes(message: Message):
    """
    Обработчик команды /get_all_wishes. Отправляет пользователю список всех его желаний.

    :param message: Сообщение от пользователя.
    """
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    wishes = await WishDao.get_all_wish_by_user(user)
    if not wishes:
        await message.answer(_('У вас еще нет пожеланий!'))
        return
    wishes_titles_str = '\n'.join(f'{index + 1}. {d(wish.title)}' for index, wish in enumerate(wishes))
    await message.answer(_('Ваши пожелания, в количестве {wishes}:\n{titles_str}').format(
        wishes=len(wishes),
        titles_str=wishes_titles_str
    ))


def _get_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для подтверждения добавления нового желания.

    :return: Объект InlineKeyboardMarkup с кнопками "Да" и "Нет".
    """
    buttons = [
        [
            InlineKeyboardButton(text=_("Да"), callback_data="w_yes"),
            InlineKeyboardButton(text=_("Нет"), callback_data="w_no")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def add_wish(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /add_wish. Начинает процесс добавления нового желания.

    :param message: Сообщение от пользователя.
    :param state: Состояние машины состояний FSMContext.
    """
    user = await UserDao.find_by_id(message.from_user.id)
    if await check_wish_limit(user):
        await state.set_state(AddWish.name)
        await message.answer(
            _("Привет, давай добавим твое желание! Напиши его"),
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(_('Вы достигли лимита пожеланий!'))
        await state.clear()


@wish_router.message(AddWish.name)
async def process_name(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает текст нового желания от пользователя.

    :param message: Сообщение от пользователя.
    :param state: Состояние машины состояний FSMContext.
    """
    if not await _add_wish(message, message.text):
        await message.answer(_('Текст должен быть не более 128 символов!'))
        await state.clear()
        return

    await state.update_data(name=message.text)
    await state.set_state(AddWish.next_wish)
    await message.answer(
        _("Прекрасно желание добавлено, {text}!\nХочешь добавить еще?").format(
            text=html.escape(message.text)),
        reply_markup=_get_keyboard()
    )


@wish_router.message(AddWish.confirm_wish)
async def confirm_wish(message: Message, state: FSMContext) -> None:
    """
    Подтверждает или отклоняет добавление нового желания.

    :param message: Сообщение от пользователя.
    :param state: Состояние машины состояний FSMContext.
    """
    user_data = await state.get_data()
    potential_wish = user_data.get('name')
    if message.text == _("Да"):
        if not await _add_wish(message, potential_wish):
            await message.answer(_('Текст должен быть не более 128 символов!'))
            await state.clear()
            return
        await state.set_state(AddWish.next_wish)
        await message.answer(
            _("Желание '{potential_wish}' добавлено. Хочешь добавить еще одно?").format(
                potential_wish=potential_wish),
            reply_markup=_get_keyboard()
        )
    elif message.text == _("Нет"):
        await state.clear()
        await get_all_wishes(message)


@wish_router.callback_query(F.data.startswith("w_"))
@wish_router.message(AddWish.next_wish)
async def handle_next_wish_decision(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает решение пользователя добавить еще одно желание.

    :param callback: Callback-запрос от пользователя.
    :param state: Состояние машины состояний FSMContext.
    """
    action = callback.data.split('_')[1]
    if action == "yes":
        user = await UserDao.find_by_id(callback.from_user.id)
        if await check_wish_limit(user):
            await state.set_state(AddWish.name)
            await callback.message.edit_text("Какое еще желание ты хотел бы добавить?")
        else:
            await callback.message.edit_text("Вы достигли лимита пожеланий!")
            await state.clear()
    elif action == "no":
        await state.clear()
        await callback.message.edit_text("Возвращаемся в меню.")


@wish_router.message(Command('edit_wish'))
async def edit_wishes(message: Message, state: FSMContext):
    """
    Начинает процесс редактирования желания.

    :param message: Сообщение от пользователя.
    :param state: Состояние машины состояний FSMContext.
    """
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    wishes = await WishDao.get_all_wish_by_user(user)
    if not wishes:
        await message.answer(_('У вас еще нет пожеланий для редактирования!'))
        return

    titles_str = '\n'.join(f'{index + 1}. {d(wish.title)}' for index, wish in enumerate(wishes))
    await message.answer(
        _('Выберите номер желания, которое хотите отредактировать:\n{titles_str}').format(titles_str=titles_str),
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddWish.edit_choice)
    await state.update_data(wishes=wishes)


@wish_router.message(AddWish.edit_choice)
async def process_edit_choice(message: Message, state: FSMContext):
    """
    Обрабатывает выбор желания для редактирования.

    :param message: Сообщение от пользователя.
    :param state: Состояние машины состояний FSMContext.
    """
    user_data = await state.get_data()
    wishes = user_data['wishes']
    choice = message.text

    if choice == '/b':
        await state.clear()
        await message.answer(_("Прекращено."))
        return

    if not choice.isdigit() or int(choice) - 1 not in range(len(wishes)):
        await message.answer(_("Пожалуйста, введите корректный номер желания.\n"
                               "/b - отмена"))
        print(choice)
        print(type(choice))
        return

    selected_wish = wishes[int(choice) - 1]
    await state.update_data(selected_wish=selected_wish)
    await message.answer(_("Введите новый текст для вашего желания:"))
    await state.set_state(AddWish.edit_text)


@wish_router.message(AddWish.edit_text)
async def process_edit_text(message: Message, state: FSMContext):
    """
    Обрабатывает новый текст для редактирования выбранного желания.

    :param message: Сообщение от пользователя.
    :param state: Состояние машины состояний FSMContext.
    """
    text = message.text
    user_data = await state.get_data()
    wish = user_data['selected_wish']
    await WishDao.update_wish(wish, text)
    await message.answer(_("Ваше желание было успешно обновлено!"))
    await state.clear()


# TODO: DELETE
@wish_router.message(Command('create'))
async def create_10_wish(message: Message):
    """
    Создает 10 пожеланий для примера.

    """
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    for i in range(10):
        await WishDao.create_wish(user=user, text=f'Пожелание #{i + 1}')

    await message.answer('Cозданно 10 желаний')
