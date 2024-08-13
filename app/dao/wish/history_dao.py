from sqlalchemy import insert, select

from app.dao.base.base_dao import BaseDao
from app.database import async_session_maker
from app.models.user.models import User
from app.models.wishes.models import WishHistory


class HistoryDao(BaseDao):
    model = WishHistory

    @classmethod
    async def create_wish_history(cls, active_wish):
        async with async_session_maker() as session:
            title = active_wish.title
            owner_id = active_wish.owner_id
            executor = active_wish.executor_id
            fulfilled = active_wish.fulfilled

            query = insert(cls.model).values(
                title=title,
                owner_id=owner_id,
                executor_id=executor,
                fulfilled=fulfilled,
            )

            await session.execute(query)
            await session.commit()

    @classmethod
    async def get_all_wish_history_by_owner(cls, user: User):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.owner_id == user.id)
            result = await session.execute(query)
            wishes = result.scalars().all()
            return wishes

    @classmethod
    async def get_all_active_wish_history_by_executor(cls, user: User):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.executor_id == user.id)
            result = await session.execute(query)
            wishes = result.scalars().all()
            return wishes

    @classmethod
    async def get_all_wish_history(cls):
        async with async_session_maker() as session:
            query = select(cls.model)
            result = await session.execute(query)
            wishes = result.scalars()
            return wishes
