from aiogram import types
from aiogram.types import FSInputFile, InputMediaPhoto

from app.config import MEDIA_DIR


# Определение пути к каталогу с медиафайлами


async def edit_callback_message(callback: types.CallbackQuery, caption: str, img_path: str,
                                reply_markup: types.InlineKeyboardMarkup) -> None:
    """
    Редактирует медиа и клавиатуру сообщения по callback.

    Аргументы:
        callback (types.CallbackQuery): Callback-запрос для ответа.
        caption (str): Заголовок для нового медиа.
        img_path (str): Относительный путь к файлу изображения.
        reply_markup (types.InlineKeyboardMarkup): Новая разметка inline-клавиатуры.
    """
    # Редактируем медиа-сообщение, заменяя его на новое изображение и заголовок
    await callback.message.edit_media(
        media=InputMediaPhoto(media=FSInputFile(MEDIA_DIR / img_path), caption=caption)
    )
    # Редактируем клавиатуру сообщения, заменяя ее на новую разметку
    await callback.message.edit_reply_markup(reply_markup=reply_markup)
    # Отвечаем на callback, чтобы уведомить пользователя, что его действие обработано
    await callback.answer()
