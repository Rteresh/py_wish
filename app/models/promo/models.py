from datetime import datetime, timedelta

from sqlalchemy import Column, String, DateTime, Boolean, BigInteger

from app.config import TIME_LIFE_PROMOCODE
from app.database import Base


class Promo(Base):
    """
    Модель промокодов.

    Атрибуты:
        id (BigInteger): Уникальный идентификатор пользователя.
        code (str): Название промокода.
        is_active (bool): Флаг, указывающий, активен ли промокод. По умолчанию True.
        created_at (datetime): Время создания промокода. По умолчанию текущее время.
        finished_at (datetime): Время завершения промокода. Может быть пустым.
    """
    __tablename__ = "promo"

    id = Column(BigInteger, primary_key=True)
    code = Column(String, index=True, default=id)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    def __init__(self, **kwargs):
        """
        Инициализирует время окончание промокода.

        Аргументы:
            kwargs (dict): Словарь с дополнительными атрибутами.
        """
        super().__init__(**kwargs)

        self.finished_at = datetime.utcnow() + timedelta(days=TIME_LIFE_PROMOCODE)
