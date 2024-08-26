from datetime import datetime, timedelta

from sqlalchemy import Column, String, DateTime, Boolean, BigInteger

from app.config import settings
from app.database import Base


class Promo(Base):
    """
    Модель промокодов.

    Атрибуты:
        id (BigInteger): Уникальный идентификатор пользователя.
        code (str): Название промокода. По умолчанию уникальный идентификатор.
        is_active (bool): Флаг, указывающий, активен ли промокод. По умолчанию True.
        created_at (datetime): Время создания промокода. По умолчанию текущее время.
        finished_at (datetime): Время завершения промокода. Может быть пустым.
    """
    __tablename__ = "promo"

    id = Column(BigInteger, primary_key=True)
    code = Column(String, index=True, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    def __init__(self, **kwargs):
        """
        Инициализация модели промокода. Устанавливает время завершения промокода.

        :param kwargs: Параметры мод
        """
        super().__init__(**kwargs)

        self.finished_at = datetime.utcnow() + timedelta(days=settings.TIME_LIFE_PROMOCODE)

    def is_valid(self):
        """
        Метод проверяет, действителен ли промокод.
        """
        return self.is_active and self.finished_at > datetime.utcnow()
