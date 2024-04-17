import asyncio
import random
from datetime import timedelta, datetime
from uuid import uuid4

from sqlalchemy import insert, update, select, or_, and_
from sqlalchemy.orm import joinedload

from app.users.models import User, Pair, PairRequest
from app.wishes.models import Wish, ActiveWish
from app.database import async_session_maker

from app.base.base_dao import BaseDao
from app.users.pair_dao import PairDao
from app.wishes.wish_dao import WishDao


class ActiveDao(BaseDao):
    model = ActiveWish

    @classmethod
    async def _get_random_time(cls):
        now = datetime.now()
        dt = timedelta(minutes=random.randint(1000, 5000))
        expired_at = now + dt
        return expired_at

    @classmethod
    async def get_active_wish_by_executor(cls, executor: User):
        async with async_session_maker() as session:
            query = select(cls.model).where(and_(
                cls.model.executor_id == executor.id,
                ActiveWish.fulfilled.__eq__(False)
            ))
            result = await session.execute(query)
            wish = result.scalars().one_or_none()
            return wish

    @classmethod
    async def get_my_active_wish(cls, user: User):
        async with async_session_maker() as session:
            wish = await cls.get_active_wish_by_executor(executor=user)
            if not wish:
                return None
            query = select(Wish).where(Wish.id == wish.wish_id)
            result = await session.execute(query)
            active_wish = result.scalars().one_or_none()
            return active_wish

    @classmethod
    async def create_active_wish(cls, user: User):
        async with async_session_maker() as session:
            partner = await PairDao.get_my_partner(user)
            if not partner:
                return None
            active_wish = await cls.get_my_active_wish(user)
            if not active_wish:
                wish = await WishDao.get_random_wish_my_partner(user)
                time = await cls._get_random_time()
                query = insert(cls.model).values(
                    executor_id=user.id,
                    owner_id=partner.id,
                    wish_id=wish.id,
                    expired_at=time
                )
                await session.execute(query)
                await session.commit()
                return wish
            return active_wish
