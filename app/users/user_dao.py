from sqlalchemy import insert, update

from app.users.models import User
from app.database import async_session_maker

from app.base.base_dao import BaseDao


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
