from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from app.database import Base


class Wish(Base):
    """
    Модель желания.

    Атрибуты:
        id (int): Уникальный идентификатор желания.
        title (str): Название желания.
        description (str): Описание желания. Может быть пустым.
        user_id (BigInteger): Идентификатор пользователя, создавшего желание.
        user (relationship): Отношение "многие к одному" с моделью User.
        created_at (datetime): Время создания желания. По умолчанию текущее время.
        fulfilled (bool): Флаг выполнения желания. По умолчанию False.
        fulfilled_at (datetime): Время выполнения желания. Может быть пустым.
        active_wishes (relationship): Отношение "один ко многим" с моделью ActiveWish.
        history_entries (relationship): Отношение "один ко многим" с моделью WishHistory.
    """
    __tablename__ = 'wishes'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    user = relationship("User", back_populates="wishes", cascade="all, delete")
    created_at = Column(DateTime, default=datetime.utcnow)
    fulfilled = Column(Boolean, default=False)
    fulfilled_at = Column(DateTime, nullable=True)
    active_wishes = relationship("ActiveWish", back_populates="wish")


class ActiveWish(Base):
    """
    Модель активного желания.

    Атрибуты:
        id (int): Уникальный идентификатор активного желания.
        title (str): Название активного желания.
        description (str): Описание активного желания. Может быть пустым.
        executor_id (BigInteger): Идентификатор пользователя, исполняющего желание.
        owner_id (BigInteger): Идентификатор пользователя, владеющего желанием.
        wish_id (BigInteger): Идентификатор связанного желания.
        created_at (datetime): Время создания активного желания. По умолчанию текущее время.
        in_confirm (bool): Флаг подтверждения выполнения желания. По умолчанию False.
        fulfilled (bool): Флаг выполнения желания. По умолчанию False.
        fulfilled_at (datetime): Время выполнения активного желания. Может быть пустым.
        expired_at (datetime): Время истечения срока действия активного желания. Может быть пустым.
        executor (relationship): Отношение "многие к одному" с моделью User для исполнителя.
        owner (relationship): Отношение "многие к одному" с моделью User для владельца.
        wish (relationship): Отношение "многие к одному" с моделью Wish.
    """
    __tablename__ = 'active_wishes'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=True)
    executor_id = Column(BigInteger, ForeignKey('users.id'))
    owner_id = Column(BigInteger, ForeignKey('users.id'))
    wish_id = Column(BigInteger, ForeignKey('wishes.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    in_confirm = Column(Boolean, default=False)
    fulfilled = Column(Boolean, default=False)
    fulfilled_at = Column(DateTime, nullable=True)
    expired_at = Column(DateTime, nullable=True)

    executor = relationship("User", cascade="all, delete", foreign_keys=[executor_id], backref="executed_active_wishes")
    owner = relationship("User", cascade='all, delete', foreign_keys=[owner_id], backref="owned_active_wishes")
    wish = relationship("Wish", back_populates="active_wishes")


class WishHistory(Base):
    """
    Модель истории желаний.

    Атрибуты:
        id (int): Уникальный идентификатор записи истории.
        title (str): Название желания.
        owner_id (BigInteger): Идентификатор пользователя, владеющего желанием.
        executor_id (BigInteger): Идентификатор пользователя, исполняющего желание.
        wish_id (BigInteger): Идентификатор связанного желания.
        fulfilled (bool): Флаг выполнения желания. По умолчанию False.
        timestamp (datetime): Время записи истории. По умолчанию текущее время.
        executor (relationship): Отношение "многие к одному" с моделью User для исполнителя.
        owner (relationship): Отношение "многие к одному" с моделью User для владельца.
        wish (relationship): Отношение "многие к одному" с моделью Wish.
    """
    __tablename__ = 'wish_histories'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    owner_id = Column(BigInteger, ForeignKey('users.id'))
    executor_id = Column(BigInteger, ForeignKey('users.id'))
    fulfilled = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    executor = relationship("User", foreign_keys=[executor_id], backref="executed_active_wishes_history")
    owner = relationship("User", foreign_keys=[owner_id], backref="owned_active_wishes_history")
