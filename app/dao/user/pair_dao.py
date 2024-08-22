import logging
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import insert, select, or_, and_, delete
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings, TIME_LIFE
from app.config import setup_logging  # noqa
from app.dao.base.base_dao import BaseDao
from app.dao.user.user_dao import UserDao
from app.database import async_session_maker
from app.models.user.models import Pair, User, PairRequest

logger = logging.getLogger("BASE_DAO")


class PairDao(BaseDao):
    model = Pair

    @classmethod
    async def get_my_pair(cls, user: User) -> Pair | None:
        """
        Возвращает пару, в которой состоит пользователь, или None, если пара не найдена.

        Args:
            user: Объект пользователя.

        Returns:
            Pair: Пара пользователя или None.
        """
        async with async_session_maker() as session:
            try:
                query = select(cls.model).where(or_(Pair.user1_id == user.id, Pair.user2_id == user.id))
                result = await session.execute(query)
                return result.scalar_one_or_none()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in get_my_pair: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in get_my_pair: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def get_partner(cls, user: User) -> User | None:
        """
        Возвращает партнера пользователя в паре или None, если пара не найдена.

        Args:
            user: Объект пользователя.

        Returns:
            User: Партнер пользователя или None.
        """
        pair = await cls.get_my_pair(user)
        if not pair:
            return None
        partner_id = pair.user2_id if pair.user1_id == user.id else pair.user1_id
        return await UserDao.find_by_id(partner_id)

    @classmethod
    async def create_pair(cls, user1: User, user2: User) -> None:
        """
        Создает новую пару с двумя пользователями.

        Args:
            user1: Первый пользователь.
            user2: Второй пользователь.

        Returns:
            None
        """
        async with async_session_maker() as session:
            try:
                query = insert(cls.model).values(user1_id=user1.id, user2_id=user2.id)
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in create_pair: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in create_pair: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def create_pair_request(cls, user: User) -> str:
        """
        Создает запрос на создание пары и возвращает ссылку для подтверждения.

        Args:
            user: Пользователь, создающий запрос.

        Returns:
            str: Ссылка для подтверждения запроса.
        """
        async with async_session_maker() as session:
            try:
                token = str(uuid4())
                confirmation_link = cls.generate_confirmation_link(token)
                query = insert(PairRequest).values(user_id=user.id, token=token)
                await session.execute(query)
                await session.commit()
                return confirmation_link

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in create_pair_request: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in create_pair_request: {e}")
                raise

            finally:
                await session.close()

    @staticmethod
    def generate_confirmation_link(token: str) -> str:
        """
        Генерирует ссылку для подтверждения запроса на создание пары.

        Args:
            token: Токен запроса.

        Returns:
            str: Ссылка для подтверждения запроса.
        """

        bot_username = settings.BOT_NAME
        return f'https://t.me/{bot_username}?start=testp_{token}'

    @classmethod
    async def get_pair_request_by_token(cls, token: str) -> PairRequest | None:
        """
        Возвращает запрос на создание пары по токену, если он активен и не истек.

        Args:
            token: Токен запроса.

        Returns:
            PairRequest: Запрос на создание пары или None.
        """
        async with async_session_maker() as session:
            try:
                query = select(PairRequest.__table__.columns).where(
                    and_(PairRequest.token == token, and_(
                        PairRequest.is_active.__eq__(True),
                        (PairRequest.created_at + timedelta(minutes=TIME_LIFE) > datetime.utcnow()  # TIME LIFE
                         )
                    )))
                result = await session.execute(query)
                return result.mappings().one_or_none()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in get_pair_request_by_token: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in get_pair_request_by_token: {e}")
                raise
            finally:
                await session.close()

    @classmethod
    async def get_partner_by_request(cls, request: PairRequest) -> User | None:
        """
        Возвращает партнера по запросу на создание пары.

        Args:
            request: Запрос на создание пары.

        Returns:
            User: Партнер или None.
        """
        if not request:
            return None
        return await UserDao.find_by_id(request.user_id)

    @classmethod
    async def confirm_pair_request(cls, user: User, partner: User):
        """
        Подтверждает запрос на создание пары, создавая пару.

        Args:
            user: Пользователь.
            partner: Партнер пользователя.

        Returns:
            None
        """
        await cls.create_pair(user1=user, user2=partner)

    @classmethod
    async def delete_pair_request(cls, pair_request: PairRequest):
        """
        Удаляет запрос на создание пары.

        Args:
            pair_request: Запрос на создание пары.

        Returns:
            None
        """
        async with async_session_maker() as session:
            try:
                query = delete(PairRequest).where(PairRequest.id == pair_request.id)
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in delete_pair_request: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in delete_pair_request: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def delete_my_pair(cls, user: User):
        """
        Удаляет пару, в которой состоит пользователь.

        Args:
            user: Пользователь, который хочет удалить пару.

        Returns:
            None
        """
        async with async_session_maker() as session:
            try:
                pair = await cls.get_my_pair(user)
                if not pair:
                    return
                query = delete(Pair).where(Pair.id == pair.id)
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in delete_my_pair: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in delete_my_pair: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def delete_timeout_pair_request(cls):
        """
        Удаляет все запросы на создание пары, срок действия которых истек.

        Метод ищет все записи в таблице PairRequest, у которых время создания
        плюс значение TIME_LIFE (в минутах) меньше текущего времени. Такие записи считаются
        устаревшими и удаляются из базы данных.

        Returns:
            None
        """
        async with async_session_maker() as session:
            try:
                query = delete(PairRequest).where(
                    PairRequest.created_at + timedelta(minutes=TIME_LIFE) < datetime.utcnow()
                )
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in delete_timeout_pair_request: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in delete_timeout_pair_request: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def get_pair_request_by_user(cls, user: User) -> PairRequest | None:
        """
        Возвращает запрос на создание пары по user, если он активен и не истек.

        Args:
            user: Пользователь.

        Returns:
            PairRequest: Запрос на создание пары или None.
        """
        async with async_session_maker() as session:
            try:
                query = select(PairRequest.__table__.columns).where(
                    and_(PairRequest.user_id == user.id, and_(
                        PairRequest.is_active.__eq__(True),
                        (PairRequest.created_at + timedelta(minutes=TIME_LIFE) > datetime.utcnow()  # TIME LIFE
                         )
                    )))
                result = await session.execute(query)
                return result.mappings().one_or_none()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in get_pair_request_by_user: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in get_pair_request_by_user: {e}")
                raise

            finally:
                await session.close()
