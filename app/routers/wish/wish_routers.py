import html

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _

from app.config import COUNT_WISH, COUNT_WISH_PREMIUM
from app.crypto.encryption_manager import _decr
from app.dao.user.user_dao import UserDao
from app.dao.wish.wish_dao import WishDao

wish_router = Router()


class AddWish(StatesGroup):
    name = State()
    next_wish = State()
    confirm_wish = State()
    edit_text = State()
    update_wish = State()
    edit_choice = State()


async def _add_wish(message: Message, text):
    data = message.from_user
    edit_text = text.lstrip('/')  # 2
    if len(edit_text) > 128:
        return False
    else:
        user = await UserDao.find_by_id(data.id)
        await WishDao.create_wish(text=edit_text, user=user)
        return True


async def check_wish_limit(user) -> bool:  # 3
    list_wish = await WishDao.get_all_wish_by_user(user)
    limit = COUNT_WISH_PREMIUM if user.is_premium else COUNT_WISH  # 4
    return len(list_wish) < limit


@wish_router.message(Command('get_all_wishes'))
async def get_all_wishes(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    wishes = await WishDao.get_all_wish_by_user(user)
    if not wishes:
        await message.answer(_('У вас еще нет пожеланий!'))
        return
    titles_str = '\n'.join(f'{index + 1}. {_decr(wish.title)}' for index, wish in enumerate(wishes))

    await message.answer(
        _('Ваши пожелания, в количестве {wishes}:\n{titles_str}').format(wishes=len(wishes), titles_str=titles_str),
    )


def _get_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text=_("Да"), callback_data="w_yes"),
            InlineKeyboardButton(text=_("Нет"), callback_data="w_no")
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


@wish_router.message(Command('add_wish'))
async def add_nwish(message: Message, state: FSMContext) -> None:
    data = message.from_user
    user = await UserDao.find_by_id(data.id)
    if await check_wish_limit(user):  # 5
        await state.set_state(AddWish.name)
        await message.answer(
            _("Привет, давай добавим твое желание! Напиши его"),
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(_('Вы достигли лимита пожеланий!'))
        await state.clear()


@wish_router.message(AddWish.name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(AddWish.next_wish)
    if not await _add_wish(message, message.text):
        await message.answer(_('Текст должен быть не более 128 символов!'))
        await state.clear()
        return
    await message.answer(
        _("Прекрасно желание добавлено, {text}!\nХочешь добавить еще?").format(
            text=html.escape(message.text)),
        reply_markup=_get_keyboard(),
    )


@wish_router.message(AddWish.confirm_wish)
async def confirm_wish(message: Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    potential_wish = user_data.get('potential_wish')
    if message.text == _("Да"):
        if not await _add_wish(message, message.text):
            await message.answer(_('Текст должен быть не более 128 символов!'))
            await state.clear()
            return
        await state.set_state(AddWish.next_wish)
        await message.answer(
            _("Желание '{potential_wish}' добавлено. Хочешь добавить еще одно?").format(potential_wish=potential_wish),
            reply_markup=_get_keyboard(),
        )
    elif message.text == _("Нет"):
        await state.clear()
        await get_all_wishes(message)


@wish_router.callback_query(F.data.startswith("w_"))
@wish_router.message(AddWish.next_wish)
async def handle_next_wish_decision(callback: types.CallbackQuery, state: FSMContext) -> None:
    action = callback.data.split('_')[1]
    if action == "yes":
        user = await UserDao.find_by_id(callback.from_user.id)  # 6
        if await check_wish_limit(user):  # 6
            await state.set_state(AddWish.name)
            await callback.message.edit_text("Какое еще желание ты хотел бы добавить?")
        else:
            await callback.message.edit_text("Вы достигли лимита пожеланий!")
            await state.clear()
    elif action == "no":
        await state.clear()
        await callback.message.edit_text("Возвращаемся в меню.")


#         Check if


# ___________________________________________________________________
# ЗДЕСЬ ФУНКЦИИИ ИЗМЕНЕНИЙ ЖЕЛАНИЙ
@wish_router.message(Command('edit_wish'))
async def edit_wishes(message: Message, state: FSMContext):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    wishes = await WishDao.get_all_wish_by_user(user)
    if not wishes:
        await message.answer(_('У вас еще нет пожеланий для редактирования!'))
        return

    titles_str = '\n'.join(f'{index + 1}. {wish.title}' for index, wish in enumerate(wishes))
    await message.answer(
        _('Выберите номер желания, которое хотите отредактировать:\n{titles_str}').format(titles_str=titles_str),
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(AddWish.edit_choice)
    await state.update_data(wishes=wishes)


@wish_router.message(AddWish.edit_choice)
async def process_edit_choice(message: Message, state: FSMContext):
    user_data = await state.get_data()
    wishes = user_data['wishes']
    choice = message.text
    if not choice.isdigit() or int(choice) - 1 not in range(len(wishes)):
        await message.answer(_("Пожалуйста, введите корректный номер желания."))
        return

    selected_wish = wishes[int(choice) - 1]
    await state.update_data(selected_wish=selected_wish)
    await message.answer(_("Введите новый текст для вашего желания:"))
    await state.set_state(AddWish.edit_text)


@wish_router.message(AddWish.edit_text)
async def process_edit_text(message: Message, state: FSMContext):
    text = message.text
    user_data = await state.get_data()
    wish = user_data['selected_wish']
    await WishDao.update_wish(wish, text)
    await message.answer(_("Ваше желание было успешно обновлено!"))
    await state.clear()
