from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    username = Column(String, index=True, default=id)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True, nullable=True)
    language = Column(String, index=True, default='ru', nullable=True)
    password = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_matched = Column(Boolean, default=False)

    wishes = relationship("Wish", back_populates="user", cascade="all, delete")
    pair_requests = relationship("PairRequest", back_populates="user", cascade="all, delete")


class Pair(Base):
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
    __tablename__ = 'pair_requests'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    token = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="pair_requests", cascade="all, delete", )

    def is_valid(self):
        return self.is_active and (datetime.utcnow() - self.created_at) < timedelta(minutes=15)
