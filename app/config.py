from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    TOKEN: str
    BOT_NAME: str
    ENCRYPTION_KEY: str

    @property
    def database_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file='/Users/rteresh/PycharmProjects/py_wish/.env', case_sensitive=False
    )


settings = Settings()
DATABASE_URL = settings.database_url

DIR = Path(__file__).absolute().parent

I18N_DOMAIN = 'bot'
LOCALES_DIR = f'{DIR}/locales'

TIME_LIFE = 10  # minutes pair request

COUNT_WISH = 3

COUNT_WISH_PREMIUM = 100

MEDIA_DIR = DIR / 'all_media'
