from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import insert, select, or_, and_, delete

from app.dao.base.base_dao import BaseDao

from app.config import settings
from app.database import async_session_maker
from app.models.user.models import Pair, User, PairRequest
from app.dao.user.user_dao import UserDao


class PairDao(BaseDao):
    model = Pair

    @classmethod
    async def get_my_pair(cls, user: User) -> Pair or None:
        async with async_session_maker() as session:
            query = select(cls.model).where(or_(Pair.user1_id == user.id, Pair.user2_id == user.id))
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_my_partner(cls, user: User) -> User:
        pair = await cls.get_my_pair(user)
        if not pair:
            return None
        partner_id = pair.user2_id if pair.user1_id == user.id else pair.user1_id
        return await UserDao.find_by_id(partner_id)

    @classmethod
    async def create_pair(cls, user1: User, user2: User) -> None:
        async with async_session_maker() as session:
            query = insert(cls.model).values(user1_id=user1.id, user2_id=user2.id)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def create_pair_request(cls, user: User) -> str:
        async with async_session_maker() as session:
            token = str(uuid4())
            bot_name = settings.BOT_NAME
            confirmation_link = f'https://t.me/{bot_name}?start=testp_{token}'  # ЗДЕСЬ URL
            query = insert(PairRequest).values(user_id=user.id, token=token)
            await session.execute(query)
            await session.commit()
            return confirmation_link

    @classmethod
    async def get_pair_request(cls, token: str) -> PairRequest or None:
        async with async_session_maker() as session:
            query = select(PairRequest.__table__.columns).where(
                and_(PairRequest.token == token, and_(
                    PairRequest.is_active.__eq__(True),
                    (PairRequest.created_at + timedelta(minutes=10) > datetime.utcnow()  # TIME LIFE
                     )
                )))
        result = await session.execute(query)
        return result.mappings().one_or_none()

    @classmethod
    async def get_partner_by_request(cls, request: PairRequest) -> User or None:
        if not request:
            return None
        partner = await UserDao.find_by_id(request.user_id)
        return partner

    @classmethod
    async def confirm_pair_request(cls, user: User, partner: User):
        await PairDao.create_pair(user1=user, user2=partner)

    @classmethod
    async def delete_pair_request(cls, pair_request: PairRequest):
        """
        Асинхронно удаляет запрос на создание пары из базы данных.

        Args:
            pair_request: Экземпляр PairRequest, который необходимо удалить.
        """
        async with async_session_maker() as session:
            query = delete(PairRequest).where(PairRequest.id == pair_request.id)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def delete_my_pair(cls, user: User):
        async with async_session_maker() as session:
            pair = await cls.get_my_pair(user)
            if not pair:
                return
            query = delete(Pair).where(Pair.id == pair.id)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def delete_timeout_pair_request(cls):
        pass
