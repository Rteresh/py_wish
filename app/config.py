import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Класс конфигурации приложения, наследующийся от BaseSettings Pydantic.

    Хранит настройки приложения, включая параметры подключения к базе данных и параметры бота.
    """

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    TOKEN: str
    BOT_NAME: str
    ENCRYPTION_KEY: str

    @property
    def database_url(self) -> str:
        """
        Формирует строку подключения к базе данных.

        :return: Строка подключения в формате URL.
        """
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file='/Users/rteresh/PycharmProjects/py_wish/.env',
        case_sensitive=False
    )


# Инициализация настроек приложения
settings = Settings()

# Строка подключения к базе данных
DATABASE_URL = settings.database_url

# Определение директорий
DIR = Path(__file__).absolute().parent

I18N_DOMAIN = 'bot'  # Домен интернационализации
LOCALES_DIR = f'{DIR}/locales'  # Директория для locales

# Настройки времени жизни запросов и лимитов
TIME_LIFE = 10  # Время жизни запроса пары в минутах
COUNT_WISH = 3  # Количество желаний для обычных пользователей
COUNT_WISH_PREMIUM = 100  # Количество желаний для премиум пользователей
TIME_LIFE_PROMOCODE = 30  # Количество дней жизни промо кода

MEDIA_DIR = DIR / 'all_media'  # Директория для хранения медиафайлов

LOGS_DIR = DIR / 'logs'  # Директория для хранения логов

MAX_WISH_LENGTH = 128  # Максимальная длина желания в символах


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Уровень логирования

    # обработчик ротации логов
    handler = RotatingFileHandler(
        LOGS_DIR / 'app.log',  # Имя файла лога
        maxBytes=5 * 1024 * 1024,  # Максимальный размер файла (5 MB)
    )
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

    # обработчик вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
