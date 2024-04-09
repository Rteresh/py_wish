from aiogram import types, Router, F
from aiogram.filters.command import Command, CommandObject
from aiogram.types import Message

from app.users.dao import create_user, get_user_by_id, get_my_pair, get_my_partner, create_wish, get_wishes_by_user_id, \
    add_active_wishes

wish_router = Router()


@wish_router.message(Command('add_wish'))
async def add_wish(message: Message, command: CommandObject):
    # Если не переданы никакие аргументы, то
    # command.args будет None
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
    await create_wish(text, message.from_user.id)
    await message.answer(
        f'Dобавлено новое пожелание: {text}'
    )


@wish_router.message(Command('get_all_wishes'))
async def get_all_wishes(message: Message):
    data = message.from_user
    wishes = await get_wishes_by_user_id(data.id)
    if not wishes:
        await message.answer('У вас еще нет пожеланий!')
        return

    titles_str = '\n'.join(f'{index + 1}. {wish.title}' for index, wish in enumerate(wishes))

    await message.answer(
        f'Ваши пожелания, в количестве {len(wishes)}:\n{titles_str}'
    )


@wish_router.message(Command('doit'))
async def get_my_wishes(message: Message):
    data = message.from_user
    active_wish = await add_active_wishes(data.id)
    if not active_wish:
        await message.answer('У вас еще нет желаний!')
        return
    await message.answer(
        f'Ваша желание: {active_wish.wish.title}'
    )
