import html

from aiogram import Router, F
from aiogram.filters.command import Command, CommandObject
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.formatting import Text
from aiogram import types
from aiogram.filters import Command, StateFilter

from aiogram.fsm.state import State, StatesGroup
from app.users.dao.user_dao import UserDao
from app.wishes.dao.wish_dao import WishDao
from aiogram.fsm.context import FSMContext

from app.wishes.dao.active_wish_dao import ActiveDao

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


class Form(StatesGroup):
    name = State()
    next_wish = State()


@wish_router.message(Command('add_wish'))
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.name)
    await message.answer(
        "Привет, давай добавим твое желание!",
        reply_markup=ReplyKeyboardRemove(),
    )


@wish_router.message(Form.name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Form.next_wish)
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
