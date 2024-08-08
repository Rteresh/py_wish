from aiogram import Router, types, F

from app.routers.menu.keyboard.main_keyboard_utils_menu import inline_main_menu
from app.routers.wish.active_wish_router import create_active_wish

start_keyboard = Router()


@start_keyboard.message(F.text.contains("Начать игру"))
async def start_game_handler(message: types.Message):
    await create_active_wish(message)
    await inline_main_menu(message)
