import asyncio
import random
from datetime import timedelta, datetime

from sqlalchemy import insert, update, select, or_, and_
from sqlalchemy.orm import joinedload

from app.users.models import User, Pair
from app.wishes.models import Wish, ActiveWish
from app.database import async_session_maker


async def create_pair(user1_id: int, user2_id: int):
    async with async_session_maker() as session:
        user1 = await get_user_by_id(user1_id)
        user2 = await get_user_by_id(user2_id)
        query = insert(Pair).values(user1_id=user1.id, user2_id=user2.id)
        await session.execute(query)
        await session.commit()
        print('well done')


# async def create_user(email: str, password: str):
#     async with async_session_maker() as session:
#         query = insert(User).values(email=email, password=password)
#         await session.execute(query)
#         await session.commit()

async def create_user(data):
    async with async_session_maker() as session:
        query = insert(User).values(
            id=data.id,
            username=data.username,
            first_name=data.first_name,
            last_name=data.last_name,
            language=data.language_code,
        )
        await session.execute(query)
        await session.commit()


async def update_email(user_id: int, new_email: str):
    async with async_session_maker() as session:
        query = update(User).where(User.id == user_id).values(email=new_email)
        await session.execute(query)
        await session.commit()


async def update_id(user_id: int, new_id: int):
    async with async_session_maker() as session:
        query = update(User).where(User.id == user_id).values(id=new_id)
        await session.execute(query)
        await session.commit()
        return new_id


async def get_user_by_id(id: int):
    async with async_session_maker() as session:
        query = select(User).where(User.id == id)
        result = await session.execute(query)
        return result.scalars().one_or_none()


async def create_wish(title: str, user_id: int):
    async with async_session_maker() as session:
        query = insert(Wish).values(title=title, user_id=user_id)
        result = await session.execute(query)
        await session.commit()


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


async def get_wishes_by_user_id(user_id: int):
    async with async_session_maker() as session:
        query = select(Wish).where(Wish.user_id == user_id)
        result = await session.execute(query)
        wishes = result.scalars().all()
        return wishes


async def get_wishes_no_fulfilled_by_user_id(user_id: int):
    async with async_session_maker() as session:
        query = select(Wish).where(and_(Wish.user_id == user_id, Wish.fulfilled.__eq__(False)))
        result = await session.execute(query)
        wishes = result.scalars().all()
        return wishes


async def get_my_partner(user_id: int):
    pair = await get_my_pair(user_id)
    if not pair:
        return None
    partner_id = pair.user2_id if pair.user1_id == user_id else pair.user1_id
    return await get_user_by_id(partner_id)


async def get_wishes_my_partner(user_id: int):
    partner = await get_my_partner(user_id)
    if not partner:
        return None
    wishes = await get_wishes_no_fulfilled_by_user_id(partner.id)
    rand = random.randrange(len(wishes))
    return wishes[rand]


async def get_random_time():
    now = datetime.now()
    dt = timedelta(minutes=random.randint(1000, 5000))
    expired_at = now + dt
    return expired_at


async def add_active_wishes(user_id: int):
    async with async_session_maker() as session:
        partner = await get_my_partner(user_id)
        if not partner:
            return None
        active_wish = await get_my_active_wish(user_id)
        if not active_wish:
            wish = await get_wishes_my_partner(user_id)
            owner = await get_my_partner(user_id)
            random_time = await get_random_time()
            query = insert(ActiveWish).values(executor_id=user_id, owner_id=owner.id, wish_id=wish.id,
                                              expired_at=random_time)
            await session.execute(query)
            await session.commit()
            return wish
        else:
            return active_wish


async def get_active_wish_by_executor_id(executor_id: int):
    async with async_session_maker() as session:
        query = select(ActiveWish).where(and_(ActiveWish.executor_id == executor_id),
                                         ActiveWish.fulfilled.__eq__(False))
        result = await session.execute(query)
        wish = result.scalars().one_or_none()
        return wish


async def get_my_active_wish(user_id: int):
    async with async_session_maker() as session:
        wish = await get_active_wish_by_executor_id(user_id)
        query = select(Wish).where(Wish.id == wish.wish_id)
        result = await session.execute(query)
        wish = result.scalars().one_or_none()
        return wish.title


async def get_partner_email(pair_id: int):
    async with async_session_maker() as session:
        query = (
            select(Pair)
            .options(joinedload(Pair.user1))
            .filter(Pair.id == pair_id)
        )
        result = await session.execute(query)
        pair = result.scalar_one_or_none()
        return pair


async def main():
    # print(await get_wishes_my_partner(1))
    # await create_user('email22@email.ru', 'string')
    # await update_email(1, 'test')
    # await create_pair(1, 2)
    # query = await get_user_by_id()
    # print(await get_user_by_id(1))
    # print(await update_id(3, 1))
    # await create_wish('test5_title_user2', 'test5_description_user2', 2)
    # print(await get_wish_by_pair(1))
    # print(await get_wishes_by_user_id(2))
    # result = await get_wish_by_pair(1)
    # print(result.id)
    # print(await get_my_pairs(1))
    # pass
    # result = await get_my_partner(2)
    # print(result.email)
    # print(await get_wishes_my_partner(1))
    # await add_active_wishes(1)
    # print(await get_my_active_wish(1))
    print(await get_partner_email(1))


if __name__ == '__main__':
    asyncio.run(main())
