from aiogram import types, Router
from aiogram.filters.command import Command
from aiogram.types import Message

base_router = Router()


@base_router.message(Command('start'))
async def bot_help(message: Message):
    await message.answer(
        f'Привет, {message.from_user}!\n'
    )
