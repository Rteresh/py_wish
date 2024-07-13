from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.i18n import gettext as _

keyboard1 = Router()


def get_main_keyboard():
    buttons = [
        [KeyboardButton(text="🎲 Начать игру")],
        [
            KeyboardButton(text="🌠 Желания"),
            KeyboardButton(text="📜 История"),
            KeyboardButton(text="💑 Пара")
        ],
        [KeyboardButton(text="🔞 Режим 18+")],
        [
            KeyboardButton(text="❓ Помощь"),
            KeyboardButton(text="⚙️ Настройки")
        ],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        one_time_keyboard=True,  # Этот параметр означает, что клавиатура будет показана только один раз
        resize_keyboard=True,
        input_field_placeholder=_("Выберите пункт меню")  # Это текст, который будет показан в поле ввода вверху экрана
    )
    return keyboard


@keyboard1.message(F.text.contains("Начать игру"))
async def start_game(message: types.Message):
    print('123')
    await message.answer("Выберите режим игры:", reply_markup=get_main_keyboard())


# def get_pair_menu():
#     pair_menu = ReplyKeyboardMarkup(resize_keyboard=True)
#     pair_menu.add(
#         KeyboardButton(text="Управление парой"),
#         KeyboardButton(text="Создать запрос"),
#         KeyboardButton(text="Просмотреть партнера"),
#         KeyboardButton(text="Отклонить партнера"),
#         KeyboardButton(text="Назад")
#     )
#     return pair_menu
#
#
# def get_wishes_menu():
#     wishes_menu = ReplyKeyboardMarkup(resize_keyboard=True)
#     wishes_menu.add(
#         KeyboardButton(text="Посмотреть все желания"),
#         KeyboardButton(text="Добавить желание"),
#         KeyboardButton(text="Удалить желание"),
#         KeyboardButton(text="Назад")
#     )
#     return wishes_menu
#
#
# def get_history_menu():
#     history_menu = ReplyKeyboardMarkup(resize_keyboard=True)
#     history_menu.add(
#         KeyboardButton(text="Просмотреть историю"),
#         KeyboardButton(text="Оценить желания"),
#         KeyboardButton(text="Назад")
#     )
#     return history_menu
#
#
# def get_support_menu():
#     support_menu = ReplyKeyboardMarkup(resize_keyboard=True)
#     support_menu.add(
#         KeyboardButton(text="Часто задаваемые вопросы (FAQ)"),
#         KeyboardButton(text="Связаться с поддержкой"),
#         KeyboardButton(text="Назад")
#     )
#     return support_menu
#
#
# def get_settings_menu():
#     settings_menu = ReplyKeyboardMarkup(resize_keyboard=True)
#     settings_menu.add(
#         KeyboardButton(text="Уведомления"),
#         KeyboardButton(text="Приватность"),
#         KeyboardButton(text="Общие настройки"),
#         KeyboardButton(text="Назад")
#     )
#     return settings_menu
#
#
# def get_18plus_menu():
#     plus_18_menu = ReplyKeyboardMarkup(resize_keyboard=True)
#     plus_18_menu.add(
#         KeyboardButton(text="Активировать подписку"),
#         KeyboardButton(text="Эксклюзивные желания"),
#         KeyboardButton(text="Настройки приватности 18+"),
#         KeyboardButton(text="Назад")
#     )
#     return plus_18_menu

@keyboard1.message(Command("rrr"))
async def command_rrr(message: types.Message):
    await message.answer("Главное меню", reply_markup=get_main_keyboard())
