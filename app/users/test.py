import asyncio
import random
from datetime import timedelta, datetime
from uuid import uuid4

from sqlalchemy import insert, update, select, or_, and_
from sqlalchemy.orm import joinedload

from app.users.models import User, Pair, PairRequest
from app.wishes.models import Wish, ActiveWish
from app.database import async_session_maker


async def get_my_partner(user_id: int):
    pair = await get_my_pair(user_id)
    if not pair:
        return None
    partner_id = pair.user2_id if pair.user1_id == user_id else pair.user1_id
    return await get_user_by_id(partner_id)


async def get_user_by_id(id: int):
    async with async_session_maker() as session:
        query = select(User).where(User.id == id)
        result = await session.execute(query)
        return result.scalars().one_or_none()


async def get_my_pair(user_id: int):
    async with async_session_maker() as session:
        user = await get_user_by_id(user_id)
        # Выбираем пользователя по его идентификатору
        query = (
            select(Pair).where(or_(Pair.user1 == user, Pair.user2 == user))
        )
        # Выполняем запрос и возвращаем результат
        result = await session.execute(query)
        return result.scalars().one_or_none()


async def create_pair(user1_id: int, user2_id: int):
    async with async_session_maker() as session:
        user1 = await get_user_by_id(user1_id)
        user2 = await get_user_by_id(user2_id)
        query = insert(Pair).values(user1_id=user1.id, user2_id=user2.id)
        await session.execute(query)
        await session.commit()


async def create_pair_request(user_id: int):
    async with async_session_maker() as session:
        pair = await get_my_pair(user_id)
        if pair:
            return 'Ты уже создаешь в паре'
        token = str(uuid4())
        query = insert(PairRequest).values(requester_id=user_id, token=token)
        await session.execute(query)
        await session.commit()
        return token


async def get_pair_request(token: str):
    async with async_session_maker() as session:
        query = (
            select(PairRequest)
        )
        result = await session.execute(query)
        return result.scalars().one_or_none()


async def accept_pair_request(token: str):
    existing_request = await get_pair_request(token)
    # if existing_request and existing_request.is_valid:
    #     print('hello')


async def main():
    # await accept_pair_request('123')
    # await get_pair_request('123')
    await get_my_partner(6)


if __name__ == '__main__':
    asyncio.run(main())
