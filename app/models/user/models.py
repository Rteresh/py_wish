from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """
    Модель пользователя.

    Атрибуты:
        id (BigInteger): Уникальный идентификатор пользователя.
        username (str): Имя пользователя. По умолчанию устанавливается равным id.
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя. Может быть пустым.
        language (str): Язык пользователя. По умолчанию 'ru'.
        password (str): Пароль пользователя. Может быть пустым.
        created_at (datetime): Время создания пользователя. По умолчанию текущее время.
        is_matched (bool): Флаг, указывающий, совпадает ли пользователь с другим пользователем. По умолчанию False.
        is_premium (bool): Флаг, указывающий, является ли пользователь премиум-пользователем. По умолчанию False.
        is_admin (bool): Флаг, указывающий, является ли пользователь администратором. По умолчанию False.
        test_promo (bool): Флаг, указывающий, имеет ли доступ к тест подписке. По умолчанию True.
        wishes (relationship): Отношение "один ко многим" с моделью Wish. Каскадное удаление.
        pair_requests (relationship): Отношение "один ко многим" с моделью PairRequest. Каскадное удаление.
    """
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    username = Column(String, index=True, default=id)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True, nullable=True)
    language = Column(String, index=True, default='ru', nullable=True)
    password = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_matched = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    time_premium = Column(DateTime, nullable=True)
    is_admin = Column(Boolean, default=False)

    test_premium = Column(Boolean, default=True)

    wishes = relationship("Wish", back_populates="user", cascade="all, delete")
    pair_requests = relationship("PairRequest", back_populates="user", cascade="all, delete")

    def is_valid_premium(self):
        """
        Проверяет действительность премиум-статуса пользователя.

        Возвращает True, если пользователь является премиум-пользователем и срок его премиум-статуса не истек.
        """
        return self.is_premium and self.time_premium > datetime.utcnow()


class Pair(Base):
    """
    Модель пары пользователей.

    Атрибуты:
        id (int): Уникальный идентификатор пары.
        user1_id (BigInteger): Идентификатор первого пользователя в паре.
        user2_id (BigInteger): Идентификатор второго пользователя в паре.
        user1 (relationship): Отношение "один к одному" с моделью User для первого пользователя. Каскадное удаление.
        user2 (relationship): Отношение "один к одному" с моделью User для второго пользователя. Каскадное удаление.
    """
    __tablename__ = 'pairs'

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(BigInteger, ForeignKey('users.id'))  # Первый пользователь в паре
    user2_id = Column(BigInteger, ForeignKey('users.id'))  # Второй пользователь в паре

    # Отношение "один к одному" с моделью User для первого пользователя
    user1 = relationship("User", foreign_keys=[user1_id], backref="pair1", cascade="all, delete",
                         primaryjoin="Pair.user1_id == User.id")

    # Отношение "один к одному" с моделью User для второго пользователя
    user2 = relationship("User", foreign_keys=[user2_id], backref="pair2", cascade="all, delete",
                         primaryjoin="Pair.user2_id == User.id")


class PairRequest(Base):
    """
    Модель запроса на создание пары.

    Args:
        id (int): Уникальный идентификатор запроса.
        user_id (BigInteger): Идентификатор пользователя, создавшего запрос.
        token (str): Уникальный токен для подтверждения запроса.
        is_active (bool): Флаг, указывающий на активность запроса. По умолчанию True.
        created_at (datetime): Время создания запроса. По умолчанию текущее время.
        user (relationship): Отношение "один к одному" с моделью User. Каскадное удаление.
    """
    __tablename__ = 'pair_requests'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    token = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="pair_requests", cascade="all, delete")

    def is_valid(self):
        """
        Проверяет действительность запроса на создание пары.

        Возвращает True, если запрос активен и создан менее 15 минут назад.
        """
        return self.is_active and (datetime.utcnow() - self.created_at) < timedelta(minutes=15)
