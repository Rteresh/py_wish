from sqlalchemy import insert, update, Boolean

from app.dao.base.base_dao import BaseDao
from app.database import async_session_maker
from app.models.user.models import User


class UserDao(BaseDao):
    model = User

    @classmethod
    async def create_user(cls, data):
        """
        Метод create_user создает новую запись пользователя в базе данных.

        Args:
            data: Объект, содержащий данные о пользователе.

        Returns:
            None
        """
        async with async_session_maker() as session:
            query = insert(cls.model).values(
                id=data.id,
                username=data.username,
                first_name=data.first_name,
                last_name=data.last_name,
                language=data.language_code,
            )
            await session.execute(query)
            await session.commit()

    @classmethod
    async def update_email(cls, user: User, new_email: str):
        """
        Метод update_email обновляет адрес электронной почты пользователя.

        Args:
            user: Объект пользователя, для которого необходимо обновить адрес электронной почты.
            new_email: Новый адрес электронной почты.

        Returns:
            None
        """
        async with async_session_maker() as session:
            query = update(User).where(User.id == user.id).values(email=new_email)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def update_premium(cls, user: User, is_premium: Boolean):
        async with async_session_maker() as session:
            query = update(User).where(User.id == user.id).values(is_premium=is_premium)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def get_username(cls, id: int):
        user = await cls.find_one_or_none(id=id)
        username = user.username
        return username
