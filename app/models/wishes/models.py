from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, TIMESTAMP, BigInteger
from sqlalchemy.orm import relationship

from app.database import Base


class Wish(Base):
    __tablename__ = 'wishes'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    # Отношение "многие к одному" с моделью User, представляющее пользователя, который создал желание
    user = relationship("User", back_populates="wishes", cascade="all, delete")
    created_at = Column(DateTime, default=datetime.utcnow)
    fulfilled = Column(Boolean, default=False)  # Флаг выполнения желания
    fulfilled_at = Column(DateTime, nullable=True)  # Время выполнения желания
    active_wishes = relationship("ActiveWish", back_populates="wish")


class ActiveWish(Base):
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

    # Отношение "многие к одному" с моделью User, представляющее исполнителя (executor)
    executor = relationship("User", cascade="all, delete", foreign_keys=[executor_id], backref="executed_active_wishes")

    # Отношение "многие к одному" с моделью User, представляющее владельца (owner)
    owner = relationship("User", cascade='all,delete', foreign_keys=[owner_id], backref="owned_active_wishes")

    # Отношение "многие к одному" с моделью Wish, представляющее текущее желание
    wish = relationship("Wish", back_populates="active_wishes")
