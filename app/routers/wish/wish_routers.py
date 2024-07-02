import html

from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

from aiogram.fsm.state import State, StatesGroup
from app.dao.user.user_dao import UserDao
from app.dao.wish.wish_dao import WishDao
from aiogram.fsm.context import FSMContext

wish_router = Router()


async def add_wish(message: Message, text):
    # Если не переданы никакие аргументы, то
    # command.args будет None
    data = message.from_user
    user = await UserDao.find_by_id(data.id)
    await WishDao.create_wish(text=text, user=user)


@wish_router.message(Command('get_all_wishes'))
async def get_all_wishes(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    wishes = await WishDao.get_wishes_by_user_id(user)
    if not wishes:
        await message.answer('У вас еще нет пожеланий!')
        return

    titles_str = '\n'.join(f'{index + 1}. {wish.title}' for index, wish in enumerate(wishes))

    await message.answer(
        f'Ваши пожелания, в количестве {len(wishes)}:\n{titles_str}'
    )


class AddWish(StatesGroup):
    name = State()
    next_wish = State()
    confirm_wish = State()
    edit_text = State()
    update_wish = State()
    edit_choice = State()


@wish_router.message(Command('add_wish'))
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(AddWish.name)
    await message.answer(
        "Привет, давай добавим твое желание! Напиши его",
        reply_markup=ReplyKeyboardRemove(),
    )


@wish_router.message(AddWish.name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(AddWish.next_wish)
    await add_wish(message, message.text)
    await message.answer(
        f"Прекрасно желание добавлено, {html.escape(message.text)}!\nХочешь добавить еще?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Да"),
                    KeyboardButton(text="Нет"),
                ]
            ],
            resize_keyboard=True,
        ),
    )


@wish_router.message(AddWish.next_wish)
async def handle_next_wish_decision(message: Message, state: FSMContext) -> None:
    if message.text == "Да":
        await state.set_state(AddWish.name)
        await message.answer("Какое еще желание ты хотел бы добавить?", reply_markup=ReplyKeyboardRemove())
    elif message.text == "Нет":
        await state.clear()
        await get_all_wishes(message)
    else:
        # Здесь мы обрабатываем случай, когда введенный текст не является ни "Да", ни "Нет"
        # Спрашиваем пользователя, является ли введенный текст его желанием
        await message.answer(
            f"'{message.text}', это твое желание? "
            f"Если да, напиши 'Да' и мы добавим это желание. "
            f"Если это была ошибка, напиши 'Нет' и мы покажем тебе список твоих желаний.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="Да"),
                        KeyboardButton(text="Нет"),
                    ]
                ],
                resize_keyboard=True,
            ),
        )
        # Сохраняем потенциальное желание в контексте состояния для возможного добавления
        await state.update_data(potential_wish=message.text)
        # Переходим в новое состояние, где будем ожидать подтверждение от пользователя
        await state.set_state(AddWish.confirm_wish)


@wish_router.message(AddWish.confirm_wish)
async def confirm_wish(message: Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    potential_wish = user_data.get('potential_wish')
    if message.text == "Да":
        # Если пользователь подтверждает, что это его желание, добавляем его
        await add_wish(message, potential_wish)
        await state.set_state(AddWish.next_wish)
        await message.answer(
            f"Желание '{potential_wish}' добавлено. Хочешь добавить еще одно?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="Да"),
                        KeyboardButton(text="Нет"),
                    ]
                ],
                resize_keyboard=True,
            ),
        )
    elif message.text == "Нет":
        # Если пользователь отказывается, выводим список его желаний
        await state.clear()
        await get_all_wishes(message)


@wish_router.message(Command('edit_wish'))
async def edit_wishes(message: Message, state: FSMContext):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    wishes = await WishDao.get_wishes_by_user_id(user)
    if not wishes:
        await message.answer('У вас еще нет пожеланий для редактирования!')
        return

    titles_str = '\n'.join(f'{index + 1}. {wish.title}' for index, wish in enumerate(wishes))
    await message.answer(
        f'Выберите номер желания, которое хотите отредактировать:\n{titles_str}',
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
        await message.answer("Пожалуйста, введите корректный номер желания.")
        return

    selected_wish = wishes[int(choice) - 1]
    await state.update_data(selected_wish=selected_wish)
    await message.answer("Введите новый текст для вашего желания:")
    await state.set_state(AddWish.edit_text)


@wish_router.message(AddWish.edit_text)
async def process_edit_text(message: Message, state: FSMContext):
    text = message.text
    user_data = await state.get_data()
    wish = user_data['selected_wish']
    await WishDao.update_wish(wish, text)
    await message.answer("Ваше желание было успешно обновлено!")
    await state.clear()
