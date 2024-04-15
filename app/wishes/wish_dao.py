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


class WishDao(BaseDao):
    model = Wish

    @classmethod
    async def create_wish(cls, title: str, user: User):
        async with async_session_maker() as session:
            query = insert(cls.model).values(
                title=title, user_id=user.id
            )
            await session.execute(query)
            await session.commit()
            print('test')

    @classmethod
    def get_wishes_by_user_id(cls, user: User):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.user_id == user.id)
            result = session.execute(query)
            wishes = result.scalars().find_one_or_none()
            return wishes


    @classmethod
    def get_unfulfilled_wishes_by_user_id(cls, user: User):
        async with async_session_maker() as session:
            pass
