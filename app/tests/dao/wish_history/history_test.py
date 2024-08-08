import os
# Добавьте корневую директорию в путь импорта
import sys
from unittest.mock import patch, AsyncMock

import pytest

from app.models.user.models import User

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from app.dao.wish.history_dao import HistoryDao
from app.models.wishes.models import WishHistory  # noqa


@pytest.mark.asyncio
@patch('app.dao.wish.history_dao.async_session_maker')
async def test_create_self_wish_history(mock_async_session_maker):
    # Мок объекта сессии
    mock_session = AsyncMock()
    mock_async_session_maker.return_value.__aenter__.return_value = mock_session

    # Мок объекта active_wish
    active_wish = AsyncMock()
    active_wish.tittle = "Test Wish"
    active_wish.owner_id = 1
    active_wish.executor_id = 2
    active_wish.wish_id = 3
    active_wish.fulfilled = False

    # Вызов тестируемого метода
    await HistoryDao.create_wish_history(active_wish)

    # Проверка, что запрос insert был вызван с правильными значениями
    mock_session.execute.assert_called_once()
    args, kwargs = mock_session.execute.call_args
    query = args[0]

    assert query.compile().params['title'] == "Test Wish"
    print(query.compile().params['title'])
    assert query.compile().params['owner_id'] == 1
    assert query.compile().params['executor_id'] == 2
    assert query.compile().params['wish_id'] == 3
    assert query.compile().params['fulfilled'] == False

    # Проверка, что commit был вызван
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
@patch('app.dao.wish.history_dao.async_session_maker')
async def test_get_all_wish_history(mock_async_session_maker):
    # Мок объекта сессии и результата выполнения запроса
    mock_session = AsyncMock()
    mock_result = AsyncMock()

    # Настраиваем mock_async_session_maker, чтобы он возвращал mock_session
    mock_async_session_maker.return_value.__aenter__.return_value = mock_session

    # Настраиваем mock_session, чтобы он возвращал mock_result при вызове execute
    mock_session.execute.return_value = mock_result

    # Настраиваем mock_result, чтобы scalars() возвращал объект с методом all()
    mock_scalars = AsyncMock()
    mock_scalars.all.return_value = [
        WishHistory(title="Test Wish 1", owner_id=1, executor_id=2, wish_id=3, fulfilled=False),
        WishHistory(title="Test Wish 2", owner_id=1, executor_id=2, wish_id=4, fulfilled=True)
    ]
    mock_result.scalars.return_value = mock_scalars

    # Вызов тестируемого метода
    wishes = await HistoryDao.get_all_wish_history()

    # Проверка, что запрос был выполнен корректно
    mock_session.execute.assert_called_once()
    args, kwargs = mock_session.execute.call_args
    query = args[0]

    # Проверка возвращаемых данных
    assert wishes[0].title == "Test Wish 1"
    assert wishes[0].owner_id == 1
    assert wishes[0].executor_id == 2
    assert wishes[0].wish_id == 3
    assert wishes[0].fulfilled == False
    assert wishes[1].title == "Test Wish 2"
    assert wishes[1].owner_id == 1
    assert wishes[1].executor_id == 2
    assert wishes[1].wish_id == 4
    assert wishes[1].fulfilled == True

    # Выводим результаты в консоль
    print(f"Retrieved wishes: {wishes}")