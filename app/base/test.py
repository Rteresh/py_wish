from aiogram import types, Router
from aiogram.filters.command import Command, CommandObject

from app.users.dao.user_dao import UserDao
from app.users.dao.pair_dao import PairDao

base_router = Router()


@base_router.message(Command(commands=["start"]))
async def process_start_command(message: types.Message, command: CommandObject):
    data = message.from_user
    args = command.args  # Получаем аргументы команды /startПолучаем аргументы команды /start
    user = await UserDao.find_by_id(data.id)
    if args and 'testp_' in args:
        token = args.split("_")[1]  # Разделяем аргументы, чтобы получить значение после testp_
        await message.answer(f'{token} вот ваш запрос')
        if user:
            partner = await PairDao.get_partner_by_request(token)
            await message.answer(f'tut {partner}')
            if partner:
                await PairDao.confirm_pair_request(token, user)
            await message.answer(
                f"Вы успешно подтвердили свою пару! "
                f"Ваш партнер: {await PairDao.find_one_or_none(user_id = user.id)}"
            )
            # pair = await PairDao.get_partner_by_request(token)
            # await message.answer(f'{pair}')

    else:
        user = await UserDao.find_by_id(data.id)
        if user:
            await message.answer(
                f"Добро пожаловать {user.first_name}!")
            return
        await UserDao.create_user(data)
        await message.answer(
            f"Добро пожаловать {await UserDao.find_by_id(data.id)}"
            f"! Если вы хотите создать пару, используйтев наш бот! "
            f"Если вы хотите создать пару, используйте команду /generate_pair_link.")
