import random
from datetime import datetime

from sqlalchemy import insert, select, and_, update

from app.models.user.models import User
from app.models.wishes.models import Wish
from app.database import async_session_maker

from app.dao.base.base_dao import BaseDao
from app.dao.user.pair_dao import PairDao


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

    @classmethod
    async def get_wishes_by_user_id(cls, user: User):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.user_id == user.id).order_by(cls.model.id.desc())
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

    @classmethod
    async def confirm_wish(cls, wish: Wish):
        async with async_session_maker() as session:
            query = update(cls.model).where(cls.model.id == wish.id).values(
                fulfilled=True,
                fulfilled_at=datetime.now(),
                description="Выполнил желание")
            await session.execute(query)
            await session.commit()

    @classmethod
    async def reject_wish(cls, wish: Wish):
        async with async_session_maker() as session:
            query = update(cls.model).where(cls.model.id == wish.id).values(
                fulfilled=True,
                fulfilled_at=datetime.now(),
                description="Не выполнил желание")
            await session.execute(query)
            await session.commit()

    @classmethod
    async def update_wish(cls, wish: Wish, text: str):
        async with async_session_maker() as session:
            query = update(cls.model).where(cls.model.id == wish.id).values(
                title=text)
            await session.execute(query)
            await session.commit()
