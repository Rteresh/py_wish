# WishBot

## Описание
`WishBot` - это Telegram-бот, который помогает парам становиться ближе, выполняя желания друг друга в формате сюрприза. Бот превращает ваши желания в увлекательную игру, добавляя элемент неожиданности и интриги в ваши отношения.

## Установка

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/Rteresh/WishBot.git
    cd WishBot
    ```

2. Создайте виртуальное окружение и активируйте его:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Windows используйте `venv\Scripts\activate`
    ```

3. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

4. Настройте переменные окружения, создайте файл `.env`:
    ```env
    TELEGRAM_TOKEN=your_telegram_bot_token
    DATABASE_URL=sqlite:///./wishbot.db
    ```

5. Выполните миграции базы данных:
    ```bash
    alembic upgrade head
    ```

## Использование

1. Запустите приложение:
    ```bash
    python main.py
    ```

2. Взаимодействуйте с ботом через Telegram:
    - Создайте список желаний.
    - Пригласите партнера.
    - Выполняйте желания друг друга в формате сюрприза.

## Тестирование

1. Установите зависимости для тестирования:
    ```bash
    pip install -r requirements-test.txt
    ```

2. Запустите тесты:
    ```bash
    pytest
    ```