from aiogram import types, Router, F
from aiogram.filters.command import Command, CommandObject
from aiogram.types import Message

from app.users.user_dao import UserDao
from app.users.pair_dao import PairDao
from app.wishes.wish_dao import WishDao
from app.wishes.active_wish_dao import ActiveDao

wish_router = Router()


@wish_router.message(Command('add_wish'))
async def add_wish(message: Message, command: CommandObject):
    # Если не переданы никакие аргументы, то
    # command.args будет None
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    if not user:
        # СЮДА ПРОПИСАТЬ ОШИБКУ
        return None
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    # Пробуем разделить аргументы на две части по первому встречному пробелу
    try:
        text = ' '.join(command.args.split(" "))
    # Если получилось меньше двух частей, вылетит ValueError
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/add_wish <message>"
        )
        return
    await WishDao.create_wish(text=text, user=user)
    await message.answer(
        f'Dобавлено новое пожелание: {text}'
    )


@wish_router.message(Command('get_all_wishes'))
async def get_all_wishes(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    if not user:
        # СЮДА ПРОПИСАТЬ ОШИБКУ
        return None
    wishes = await WishDao.get_wishes_by_user_id(user)
    if not wishes:
        await message.answer('У вас еще нет пожеланий!')
        return

    titles_str = '\n'.join(f'{index + 1}. {wish.title}' for index, wish in enumerate(wishes))

    await message.answer(
        f'Ваши пожелания, в количестве {len(wishes)}:\n{titles_str}'
    )


@wish_router.message(Command('doit'))
async def get_my_wishes(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    if not user:
        # СЮДА ПРОПИСАТЬ ОШИБКУ
        return None
    active_wish = await ActiveDao.create_active_wish(user)
    if not active_wish:
        await message.answer('У вас еще нет желаний!')
        return
    await message.answer(
        f'Ваша желание: {active_wish.title}'
        f'Ваша желание: {active_wish.id}'
    )
