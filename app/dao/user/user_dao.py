import logging
from datetime import timedelta, datetime

from sqlalchemy import insert, update, select, and_
from sqlalchemy.exc import SQLAlchemyError

from app.dao.base.base_dao import BaseDao
from app.database import async_session_maker
from app.models.user.models import User

logger = logging.getLogger("USER_DAO")


class UserDao(BaseDao):
    model = User

    @classmethod
    async def create_user(cls, data):
        """
        Метод создает новую запись пользователя в базе данных.

        Args:
            data: Объект, содержащий данные о пользователе.
            Ожидаются атрибуты id, username, first_name, last_name, language_code.

        Returns:
            None
        """
        async with async_session_maker() as session:
            try:
                query = insert(cls.model).values(
                    id=data.id,
                    username=data.username,
                    first_name=data.first_name,
                    last_name=data.last_name,
                    language=data.language_code,
                )
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in get_pair_request_by_token: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred while creating user: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def update_email(cls, user: User, new_email: str):
        """
        Метод обновляет адрес электронной почты пользователя.

        Args:
            user: Объект пользователя, для которого необходимо обновить адрес электронной почты.
            new_email: Новый адрес электронной почты.

        Returns:
            None
        """
        async with async_session_maker() as session:
            try:
                query = update(User).where(User.id == user.id).values(email=new_email)
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in update_email: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in update_email: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def update_premium(cls, user: User, is_premium: bool, time: int):
        """
        Метод обновляет статус премиум-подписки пользователя.

        Args:
            user: Объект пользователя, для которого необходимо обновить статус.
            is_premium: Логическое значение, указывающее на наличие премиум-подписки.
            time: Длительность премиум-подписки в днях.

        Returns:
            None
        """
        async with async_session_maker() as session:
            try:
                if user.time_premium and user.is_valid_premium():
                    time_premium = user.time_premium + timedelta(days=time * 30)
                else:
                    time_premium = datetime.utcnow() + timedelta(days=time * 30)
                query = update(User).where(User.id == user.id).values(
                    is_premium=is_premium,
                    time_premium=time_premium)
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in update_premium: {e}")

            except Exception as e:
                logger.error(f"An unexpected error occurred in update_premium: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def update_test_premium(cls, user: User, is_premium: bool):
        """
        Метод обновляет статус тестовой премиум-подписки пользователя.
        :param user: Модель пользователя
        :param is_premium: Логическое значение, указывающее на наличие тестовой премиум-подписки.
        """
        async with async_session_maker() as session:
            try:
                query = update(User).where(User.id == user.id).values(
                    test_premium=is_premium
                )
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in update_test_premium: {e}")

            except Exception as e:
                logger.error(f"An unexpected error occurred in update_test_premium: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def get_username(cls, user_id: int):
        """
        Метод возвращает имя пользователя по его идентификатору.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            str: Имя пользователя или None, если пользователь не найден.
        """
        user = await cls.find_one_or_none(id=user_id)
        if user is None:
            return None
        return user.username

    @classmethod
    async def get_language(cls, user_id: int):
        """
        Метод возвращает язык пользователя по его идентификатору.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            str: Язык пользователя или None, если пользователь не найден.
        """
        user = await cls.find_one_or_none(id=user_id)
        if user is None:
            return None
        return user.language

    @classmethod
    async def update_language(cls, user_id: int, new_language: str):
        """
        Метод обновляет язык пользователя.

        Args:
            user_id: Идентификатор пользователя.
            new_language: Новый язык пользователя.

        Returns:
            None
        """
        async with async_session_maker() as session:
            try:
                query = update(User).where(User.id == user_id).values(language=new_language)
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in update_language: {e}")

            except Exception as e:
                logger.error(f"An unexpected error occurred in update_language: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def check_premium(cls, user_id: int) -> datetime:
        """
        Метод проверяет статус премиум-подписки пользователя.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            datetime: Время окончания премиум-подписки пользователя или None, если подписка не активна.
        """
        user = await cls.find_one_or_none(id=user_id)
        if user is None:
            return None
        return user.time_premium

    @classmethod
    async def get_finished_premium_users(cls) -> list:
        """
        Метод возвращает список пользователей, у которых закончилась премиум-подписка.

        Returns:
            list: Список пользователей, у которых закончилась премиум-подписка.
        """
        async with async_session_maker() as session:
            try:
                query = select(cls.model).where(
                    and_(cls.model.time_premium < datetime.utcnow(), cls.model.is_premium == True)
                )
                result = await session.execute(query)
                users = result.scalars().all()
                return users

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in get_finished_premium_users: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in get_finished_premium_users: {e}")
                raise

            finally:
                await session.close()
