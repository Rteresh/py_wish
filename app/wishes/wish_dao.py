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


class WishDao(BaseDao):
    model = Wish

    @classmethod
    async def create_wish(cls, text: str, user: User):
        async with async_session_maker() as session:
            query = insert(cls.model).values(
                title=text, user_id=user.id
            )
            await session.execute(query)
            await session.commit()
            print('test')

    @classmethod
    async def get_wishes_by_user_id(cls, user: User):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.user_id == user.id)
            result = await session.execute(query)
            wishes = result.scalars().all()
            return wishes

    @classmethod
    async def get_unfulfilled_wishes_by_user_id(cls, user: User):
        async with async_session_maker() as session:
            query = select(cls.model).where(
                and_(
                    cls.model.user_id == user.id,
                    cls.model.fulfilled.__eq__(False))
            )
            result = await session.execute(query)
            wishes = result.scalars().all()
            return wishes

    @classmethod
    async def get_wishes_my_partner(cls, user: User):
        partner = await PairDao.get_my_partner(user)
        if not partner:
            return None
        wishes = await cls.get_unfulfilled_wishes_by_user_id(partner)
        return wishes

    @classmethod
    async def get_random_wish_my_partner(cls, user: User):
        partner = await PairDao.get_my_partner(user)
        if not partner:
            return None
        wishes = await cls.get_unfulfilled_wishes_by_user_id(partner)
        rand = random.randrange(len(wishes))
        return wishes[rand]
