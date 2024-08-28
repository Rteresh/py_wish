from aiogram import types
from aiogram.types import FSInputFile, InputMediaPhoto

from app.config import MEDIA_DIR
from app.dao.wish.active_wish_dao import ActiveDao
from app.dao.wish.history_dao import HistoryDao
from app.dao.wish.wish_dao import WishDao


# Определение пути к каталогу с медиафайлами


async def edit_callback_message(callback: types.CallbackQuery, caption: str, img_path: str,
                                reply_markup: types.InlineKeyboardMarkup or None) -> None:
    """
    Редактирует медиа и клавиатуру сообщения по callback.

    Args:
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


async def reject_wish(active_wish, user):
    """
    Отклоняет желание партнеру и переносит его в историю.

    :param active_wish: Объект активного желания
    :param user: Объект пользователя [хозяин или исполнитель]

    """
    # Получаем желание по его ID
    wish = await WishDao.find_by_id(active_wish.wish_id)

    # Отклонение активного желания пользователем
    await ActiveDao.reject_active_wish(user)

    # Обновление активного желания после принятия
    update_wish = await ActiveDao.find_by_id(active_wish.id)

    # Создание записи в истории
    await HistoryDao.create_wish_history(update_wish)

    # Удаление активного желания
    await ActiveDao.delete_by_id(active_wish.id)

    # Удаление самого желания
    await WishDao.delete_by_id(wish.id)


async def accept_wish(active_wish, user):
    """
    Принимает желание партнера и переносит его в историю.

    :param active_wish: Объект активного желания.
    :param user: Объект пользователя (хозяин или исполнитель).
    """
    # Получаем желание по его ID
    wish = await WishDao.find_by_id(active_wish.wish_id)

    # Принятие активного желания пользователем
    await ActiveDao.accept_active_wish(user)

    # Обновление активного желания после принятия
    update_wish = await ActiveDao.find_by_id(active_wish.id)

    # Создание записи в истории
    await HistoryDao.create_wish_history(update_wish)

    # Удаление активного желания
    await ActiveDao.delete_by_id(active_wish.id)

    # Удаление самого желания
    await WishDao.delete_by_id(wish.id)

