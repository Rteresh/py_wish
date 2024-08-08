from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from app.dao.user.user_dao import UserDao
from app.dao.wish.history_dao import HistoryDao

history_router = Router()


@history_router.message(Command('get_history_owner'))
async def get_wish_history_owner(message: Message, page: int = 1):
    """
    Обработчик команды для получения истории желаний владельца.

    Запрашивает историю желаний для владельца и отображает её с пагинацией.

    :param message: Сообщение пользователя с командой.
    :param page: Номер страницы (по умолчанию 1).
    """
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    await _paginate(message, page, HistoryDao.get_all_wish_history_by_owner, user, command='owner')


@history_router.message(Command('get_history_executor'))
async def get_wish_history_executor(message: Message, page: int = 1):
    """
    Обработчик команды для получения истории желаний исполнителя.

    Запрашивает историю желаний для исполнителя и отображает её с пагинацией.

    :param message: Сообщение пользователя с командой.
    :param page: Номер страницы (по умолчанию 1).
    """
    user = await UserDao.find_one_or_none(id=message.from_user.id)
    await _paginate(message, page, HistoryDao.get_all_active_wish_history_by_executor, user, command='executor')


async def _get_pagination_keyboard(page: int, total_pages: int, command: str) -> InlineKeyboardMarkup:
    """
    Генерация клавиатуры для пагинации.

    Создает клавиатуру с кнопками "Prev" и "Next" для навигации по страницам.

    :param page: Текущая страница.
    :param total_pages: Общее количество страниц.
    :param command: Команда для определения типа истории (owner или executor).
    :return: InlineKeyboardMarkup с кнопками пагинации.
    """
    buttons = []

    if page > 1:
        buttons.append(InlineKeyboardButton(text=_('Prev'), callback_data=f'{command}_prev_{page}'))

    if page < total_pages:
        buttons.append(InlineKeyboardButton(text=_('Next'), callback_data=f'{command}_next_{page}'))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard


async def _paginate(message: Message, page: int, get_history_func, user, command: str):
    """
    Пагинация и отображение истории желаний в виде таблицы.

    Запрашивает данные истории и отображает их в виде таблицы с пагинацией.

    :param message: Сообщение, на которое нужно ответить.
    :param page: Текущая страница.
    :param get_history_func: Функция для получения истории.
    :param user: Объект пользователя, для которого запрашивается история.
    :param command: Команда для определения типа истории (owner или executor).
    """
    history = await get_history_func(user)
    if not history:
        await message.answer('У вас нету историй')
        return

    items_per_page = 10

    total_items = len(history)
    total_pages = (total_items + items_per_page - 1) // items_per_page

    start_index = (page - 1) * items_per_page
    end_index = min(start_index + items_per_page, total_items)

    table_header = _("No | Title | TEST_NAME | Fulfilled | Closed Date")
    if command == 'executor':
        table_rows = [
            _('{}. | {} | {} | {} | {}').format(
                i + 1,
                history[i].title,
                await UserDao.get_username(history[i].owner_id),
                _('Yes') if history[i].fulfilled else _('No'),
                history[i].timestamp.strftime('%Y-%m-%d %H:%M:%S')
            ) for i in range(start_index, end_index)
        ]
    else:
        table_rows = [
            _('{}. | {} | {} | {} | {}').format(
                i + 1,
                history[i].title,
                await UserDao.get_username(history[i].executor_id),
                _('Yes') if history[i].fulfilled else _('No'),
                history[i].timestamp.strftime('%Y-%m-%d %H:%M:%S')
            ) for i in range(start_index, end_index)
        ]

    message_text = "\n".join([table_header] + table_rows)

    keyboard = await _get_pagination_keyboard(page, total_pages, command)
    await message.answer(message_text, reply_markup=keyboard)


@history_router.callback_query(F.data.startswith(('owner_', 'executor_')))
async def handle_pagination(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик пагинации для кнопок "Prev" и "Next".

    Обрабатывает нажатия на кнопки пагинации и обновляет отображение истории.

    :param callback_query: Объект CallbackQuery.
    :param state: Состояние FSMContext.
    """
    data = callback_query.data.split('_')
    command = data[0]
    action = data[1]
    current_page = int(data[2])

    if action == 'prev':
        new_page = max(current_page - 1, 1)
    elif action == 'next':
        new_page = current_page + 1
    else:
        new_page = current_page

    await callback_query.message.delete()

    user = await UserDao.find_one_or_none(id=callback_query.from_user.id)

    if command == 'owner':
        get_history_func = HistoryDao.get_all_wish_history_by_owner
    elif command == 'executor':
        get_history_func = HistoryDao.get_all_active_wish_history_by_executor
    else:
        return

    await _paginate(callback_query.message, new_page, get_history_func, user, command=command)
