import asyncio
import random
from datetime import timedelta, datetime
from uuid import uuid4

from sqlalchemy import insert, update, select, or_, and_
from sqlalchemy.orm import joinedload

from app.users.models import User, Pair, PairRequest
from app.wishes.models import Wish, ActiveWish
from app.database import async_session_maker


async def create_pair_request(user_id: int):
    async with async_session_maker() as session:
        token = str(uuid4())
        query = insert(PairRequest).values(requester_id=user_id, token=token)
        result = await session.execute(query)
        await session.commit()
        return result.scalars().one_or_none()


async def get_pair_by_token(token: str):
    pass
