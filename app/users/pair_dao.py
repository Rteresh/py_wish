from uuid import uuid4

from sqlalchemy import insert, update, select, or_, and_

from app.database import async_session_maker
from app.base.base_dao import BaseDao
from app.users.models import Pair, User, PairRequest
from app.users.user_dao import UserDao


class PairDao(BaseDao):
    model = Pair

    @classmethod
    async def get_my_pair(cls, user: User):
        async with async_session_maker as session:
            query = select(Pair).where(or_(Pair.user1 == user, Pair.user2 == user))
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_my_partner(cls, user: User):
        pair = await cls.get_my_pair(user)
        if not pair:
            return None
        partner_id = pair.user2_id if pair.user1_id == user.id else pair.user1_id
        return await UserDao.find_by_id(partner_id)

    @classmethod
    async def create_pair(cls, user1: User, user2: User):
        async with async_session_maker() as session:
            user1 = await UserDao.find_by_id(user1)
            user2 = await UserDao.find_by_id(user2)
            query = insert(Pair).values(user1_id=user1.id, user2_id=user2.id)
            await session.execute(query)
            await session.commit()
            print('Pair created')

    @classmethod
    async def create_pair_request(cls, user: User):
        async with async_session_maker() as session:
            pair = await cls.get_my_pair(user)
            if pair:
                return 'Ты уже создаешь в паре'
            token = str(uuid4())
            query = insert(PairRequest).values(user_id=user.id, token=token)
            await session.execute(query)
            await session.commit()