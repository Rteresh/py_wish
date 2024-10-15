FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем необходимые системные зависимости для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip до последней версии
RUN pip install --upgrade pip

# Копируем все файлы приложения в контейнер
COPY . /app

# Копируем .env файл
COPY . .env

# Устанавливаем необходимые зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем оставшиеся файлы проекта в контейнер
COPY . .

# Указываем переменные окружения для доступа к базе данных и конфигурации
ENV PYTHONUNBUFFERED 1

# Открываем порт для работы FastAPI
EXPOSE 8000
# Указываем команду для запуска вашего приложения
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8000"]