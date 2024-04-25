from aiogram import types, Router
from aiogram.filters.command import Command, CommandObject

from app.users.models import PairRequest, User
from app.users.dao.user_dao import UserDao
from app.users.dao.pair_dao import PairDao

base_router = Router()


@base_router.message(Command(commands=["start"]))
async def process_start_command(message: types.Message, command: CommandObject):
    data = message.from_user
    args = command.args
    user = await UserDao.find_by_id(data.id)
    url_api = 'testp_'
    if not user:
        await UserDao.create_user(data)
        await message.answer(
            'Вы успешно зарегистрированы!'
        )
        user = await UserDao.find_by_id(data.id)
        pair_request = await check_pair_request(args, url_api, message)
        if pair_request:
            await confirm_pair_request(message, pair_request, user)
    else:
        if await check_pair(user):
            pair_request = await check_pair_request(args, command, message)
            if pair_request:
                await confirm_pair_request(message, pair_request, user)
        else:
            await message.answer(
                'Вы уже состоите в паре!'
            )


async def check_pair_request(args: str, url_api: str, message: types.Message) -> PairRequest or None:
    if args and 'testp_' in args:
        token = args.split('_')[1]
        pair_request = await PairDao.get_pair_request(token)
        if not pair_request:
            await message.answer(
                'Запрос на пару не найден или недействительный'
            )
            return None
        return pair_request


async def confirm_pair_request(message: types.Message, pair_request: PairRequest, user: User):
    partner = await PairDao.get_partner_by_request(pair_request)
    if not partner:
        await message.answer(
            'Партнер не найден'
        )
    else:
        await PairDao.confirm_pair_request(user, partner)
        await PairDao.delete_pair_request(pair_request)
        await message.answer(
            'Вы успешно подтвердили свою пару!'
        )


async def check_pair(user: User) -> bool:
    pair = await PairDao.get_my_pair(user)
    if pair:
        return False
    return True



