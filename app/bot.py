import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.types import BotCommand

from app.config import settings
from app.routers.user.user_router import user_router
from app.routers.base.base_router import base_router
from app.routers.wish.wish_routers import wish_router
from app.routers.user.pair_router import pair_router
from app.routers.menu.menu_router import menu_router
from app.routers.wish.active_wish_router import active_router, alert_timeout_active
from app.dao.wish.test import test_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.TOKEN)
dp = Dispatcher()

main_router = Router()
main_router.include_router(user_router)
main_router.include_router(base_router)
main_router.include_router(wish_router)
main_router.include_router(pair_router)
main_router.include_router(menu_router)
main_router.include_router(active_router)
main_router.include_router(test_router)
dp.include_router(main_router)



async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начать"),
        BotCommand(command="create_pair", description="Создать запрос на пару"),
        BotCommand(command="get_pair", description="Посмотреть на своего партнера"),
        BotCommand(command="reject_pair", description="Отклонить текущего партнера"),
        BotCommand(command="add_wish", description="Добавить желание"),
        BotCommand(command="doit", description="Хочу выполнить желание партнера"),
        BotCommand(command="add_active_wish", description="Добавить активное желание"),
        BotCommand(command="get_active_wish", description="Посмотреть активное желание"),
        BotCommand(command="get_all_wishes", description="Посмотреть все мои желания"),
        BotCommand(command="get_time", description="Посмотреть оставшиеся время"),
        BotCommand(command="done", description="Выполнил желание партнера"),
    ]
    await bot.set_my_commands(commands)


#
# from aiogram import types
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
#
# from aiogram.types import Message
#
#
# # Команда для отправки сообщения с кнопками
# # Команда для отправки сообщения с кнопками
# @dp.message(Command('test'))
# async def send_confirmation_request(message: types.Message):
#     # Создаем кнопки
#     buttons = [
#         InlineKeyboardButton(text="Подтвердить", callback_data="confirm", cache_time=0),
#         InlineKeyboardButton(text="Отклонить", callback_data="reject", cache_time=0)
#     ]
#     # Создаем клавиатуру и передаем список кнопок
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
#     await bot.send_message(message.from_user.id, "Пожалуйста, подтвердите выполнение желания.", reply_markup=keyboard)
#
#
# # Обработчик нажатий на кнопки
# @dp.callback_query(lambda c: c.data in ['confirm', 'reject'])
# async def process_callback(callback_query: CallbackQuery):
#     action = callback_query.data
#     if action == "confirm":
#         response_text = "Вы подтвердили действие."
#         print('Вы подтвердили действие.')
#     else:
#         response_text = "Вы отклонили действие."
#         print('Вы отклонили действие.')
#
#     await callback_query.answer()  # Уведомление Telegram, что callback получен
#     # Обновляем сообщение, удаляя клавиатуру
#     await bot.edit_message_text(chat_id=callback_query.from_user.id,
#                                 message_id=callback_query.message.message_id,
#                                 text=response_text,
#                                 reply_markup=None)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
    asyncio.run(set_commands(bot))
    asyncio.create_task(alert_timeout_active(bot))
