from aiogram import types, Router
from aiogram.filters.command import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

from app.dao.user.pair_dao import PairDao
from app.dao.user.user_dao import UserDao
from app.models.user.models import PairRequest, User
from app.routers.menu.language_router import set_language
from app.routers.state.states import Form

base_router = Router()


@base_router.message(Command(commands=["start"]))
async def process_start_command(message: types.Message, command: CommandObject, state: FSMContext):
    data = message.from_user
    args = command.args
    user = await UserDao.find_by_id(data.id)
    url_api = 'testp_'
    if not user:
        await handle_new_user(data, message, args, url_api)
    else:
        await handle_existing_user(user, message, args, command)

    await state.set_state(Form.choosing_language)
    await state.update_data(from_start=True)
    await set_language(message, state)


async def handle_new_user(data, message, args, url_api):
    await UserDao.create_user(data)
    await message.answer(_('Вы успешно зарегистрированы!'))
    user = await UserDao.find_by_id(data.id)
    pair_request = await check_pair_request(args, url_api, message)
    if pair_request:
        await confirm_pair_request(message, pair_request, user)


async def handle_existing_user(user, message, args, command):
    if await check_pair(user):
        pair_request = await check_pair_request(args, command, message)
        if pair_request:
            await confirm_pair_request(message, pair_request, user)
    else:
        await message.answer(_('Вы уже состоите в паре!'))


async def check_pair_request(args: str, url_api: str, message: types.Message) -> PairRequest or None:
    if args and 'testp_' in args:
        token = args.split('_')[1]
        pair_request = await PairDao.get_pair_request(token)
        if not pair_request:
            await message.answer(
                _('Запрос на пару не найден или недействительный')
            )
            return None
        return pair_request


async def confirm_pair_request(message: types.Message, pair_request: PairRequest, user: User):
    partner = await PairDao.get_partner_by_request(pair_request)
    if not partner:
        await message.answer(
            _('Партнер не найден')
        )
    elif user.id == partner.id:
        await message.answer(
            _(f"Нельзя создать пару с самим собой! ")
        )
        return
    else:
        await PairDao.confirm_pair_request(user, partner)
        await PairDao.delete_pair_request(pair_request)
        await message.answer(
            _('Вы успешно подтвердили свою пару!')
        )


async def check_pair(user: User) -> bool:
    pair = await PairDao.get_my_pair(user)
    if pair:
        return False
    return True

# ---------- Выбор языка
