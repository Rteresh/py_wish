import random
from datetime import timedelta, datetime

from sqlalchemy import insert, select, and_, update

from app.models.user.models import User
from app.models.wishes.models import Wish, ActiveWish
from app.database import async_session_maker

from app.dao.base.base_dao import BaseDao
from app.dao.user.pair_dao import PairDao
from app.dao.wish.wish_dao import WishDao


class ActiveDao(BaseDao):
    model = ActiveWish

    @classmethod
    async def _get_random_time(cls):
        now = datetime.now()
        dt = timedelta(minutes=random.randint(1000, 5000))
        expired_at = now + dt
        return expired_at

    @classmethod
    async def get_active_wish_by_executor(cls, executor: User) -> ActiveWish or None:
        async with async_session_maker() as session:
            query = select(cls.model).where(and_(
                cls.model.executor_id == executor.id,
                ActiveWish.fulfilled.__eq__(False)
            ))
            result = await session.execute(query)
            wish = result.scalars().first()
            return wish

    @classmethod
    async def get_my_active_wish(cls, user: User) -> ActiveWish or None:
        async with async_session_maker() as session:
            wish = await cls.get_active_wish_by_executor(executor=user)
            if not wish:
                return None
            query = select(Wish).where(Wish.id == wish.wish_id)
            result = await session.execute(query)
            wish = result.scalars().one_or_none()
            return wish

    @classmethod
    async def create_active_wish(cls, user: User):
        async with async_session_maker() as session:
            partner = await PairDao.get_my_partner(user)
            wish = await WishDao.get_random_wish_my_partner(user)
            time = await cls._get_random_time()
            query = insert(cls.model).values(
                executor_id=user.id,
                owner_id=partner.id,
                wish_id=wish.id,
                expired_at=time,
                title=wish.title,
            )
            await session.execute(query)
            await session.commit()

    @classmethod
    async def confirm_active_wish(cls, user: User):
        async with async_session_maker() as session:
            wish = await cls.get_my_active_wish(user)
            await WishDao.confirm_wish(wish)
            query = update(cls.model).where(cls.model.executor_id == user.id).values(
                fulfilled=True,
                fulfilled_at=datetime.now(),
                description="Выполнил желание"
            )
            await session.execute(query)
            await session.commit()

    @classmethod
    async def reject_active_wish(cls, executor: User):
        async with async_session_maker() as session:
            wish = await cls.get_my_active_wish(executor)
            await WishDao.confirm_wish(wish)
            query = update(cls.model).where(cls.model.executor_id == executor.id).values(
                fulfilled=True,
                fulfilled_at=datetime.now(),
                description="Не выполнил желание"
            )
            await session.execute(query)
            await session.commit()

    @classmethod
    async def get_all_unfulfilled_wish(cls) -> list[ActiveWish]:
        async with async_session_maker() as session:
            query = select(cls.model).where(and_(
                cls.model.fulfilled.__eq__(False),
                cls.model.expired_at.__lt__(datetime.now())
            ))
            result = await session.execute(query)
            wishes = result.scalars().all()
            return wishes
