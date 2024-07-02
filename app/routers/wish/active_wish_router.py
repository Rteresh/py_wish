from asyncio import sleep
from datetime import datetime

from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from app.dao.user.pair_dao import PairDao
from app.dao.user.user_dao import UserDao
from app.models.user.models import User
from app.dao.wish.active_wish_dao import ActiveDao

active_router = Router()


@active_router.message(Command('doit'))
async def create_active_wish(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    if await _check_active_wish(user):
        await get_active(user, message)
    else:
        await ActiveDao.create_active_wish(user)
        await get_active(user, message)


async def _check_active_wish(user) -> bool:
    active_wish = await ActiveDao.get_active_wish_by_executor(user)
    if not active_wish:
        return False
    return True


async def get_active(user: User, message: Message):
    active_wish = await ActiveDao.get_active_wish_by_executor(user)
    if not active_wish:
        await message.answer('У вас еще нет активного желания')
        return
    await message.answer(
        f'Ваша желание: {active_wish.title}\n'
        f'Срок на выполнение:{active_wish.expired_at}\n'
    )


@active_router.message(Command('get_active_wish'))
async def get_active_wish(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    await get_active(user, message)


@active_router.message(Command('get_time'))
async def get_active_time(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    active_wish = await ActiveDao.get_active_wish_by_executor(user)
    if not active_wish:
        await message.answer('У вас еще нет активного желания')
        return

    days, hours, minutes = await _get_time_until_expiration(active_wish.expired_at)
    await message.answer(
        f'Ваше желание: {active_wish.title}\n'
        f'Вам осталось {days} дней {hours} часов {minutes} минут до истечения срока.\n'
    )


async def _get_time_until_expiration(expiration_date: datetime):
    now = datetime.now()
    # Разница между датой истечения срока и текущим временем
    time_delta = expiration_date - now
    # Преобразование разницы в дни, часы и минуты
    days = time_delta.days
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return days, hours, minutes


@active_router.message(Command('done'))
async def send_confirmation_request(message: Message):
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    if not await _check_active_wish(user):
        await message.answer('У вас еще нет активного желания')
        return
    wish = await ActiveDao.get_active_wish_by_executor(user)
    partner = await PairDao.get_my_partner(user)
    buttons = [
        InlineKeyboardButton(text="Подтвердить", callback_data="confirm", cache_time=0),
        InlineKeyboardButton(text="Отклонить", callback_data="reject", cache_time=0)
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    await message.bot.send_message(partner.id, f"Пожалуйста, подтвердите выполнение желания: {wish.title}\n"
                                               f"Выполнил: {user.username}.",
                                   reply_markup=keyboard)


@active_router.callback_query(lambda c: c.data in ['confirm', 'reject'])
async def process_callback(callback_query: CallbackQuery):
    action = callback_query.data
    user = await UserDao.find_one_or_none(id=callback_query.from_user.id)
    partner = await PairDao.get_my_partner(user)
    wish = await ActiveDao.get_my_active_wish(partner)
    if action == "confirm":
        if wish:
            response_text = "Вы подтвердили действие."
            await ActiveDao.confirm_active_wish(partner)
            await _send_accept_request(callback_query.bot, partner, user)
        else:
            response_text = "Запрос был уже выполнен"
    else:
        if wish:
            response_text = "Вы отклонили действие."
            await ActiveDao.reject_active_wish(partner)
        else:
            response_text = "Запрос был уже выполнен"

    await callback_query.answer()  # Уведомление Telegram, что callback получен
    # Обновляем сообщение, удаляя клавиатуру
    await callback_query.bot.edit_message_text(chat_id=user.id,
                                               text=response_text,
                                               message_id=callback_query.message.message_id,
                                               reply_markup=None)


async def alert_timeout_active(bot):
    while True:
        active_wishes = await ActiveDao.get_all_unfulfilled_wish()
        for active_wish in active_wishes:
            owner = await UserDao.find_one_or_none(id=active_wish.owner_id)
            executor = await UserDao.find_one_or_none(id=active_wish.executor_id)
            await bot.send_message(owner.id, f"Ваше желание {active_wish.title} не выполнено,\n"
                                             f" партнером:{executor.username}. "
                                   )
            await sleep(10)
            await bot.send_message(owner.id, f"Ваше желание {active_wish.title} не выполнено,\n"
                                             f" партнером:{executor.username}.")
            await ActiveDao.reject_active_wish(executor)
            print('well done')


@active_router.message(Command('test1'))
async def get_test(message: Message):
    active_wishes = await ActiveDao.get_all_unfulfilled_wish()
    for active_wish in active_wishes:
        owner = await UserDao.find_one_or_none(id=active_wish.owner_id)
        executor = await UserDao.find_one_or_none(id=active_wish.executor_id)
        await message.answer(f"Ваше желание {active_wish.title} не выполнено,\n"
                             f" партнером:{executor.username}. "
                             )
        await sleep(10)
        await message.answer(f"Ваше желание {active_wish.title} не выполнено,\n"
                             f" партнером:{executor.username}."
                             )


async def _send_accept_request(bot, partner, user):
    await bot.send_message(partner.id, f" 'Спасибо большое, что выполнил мое желание' "
                                       f"с любовью от партнера {user.username}.\n")
