import logging
import random
from datetime import timedelta, datetime

from sqlalchemy import insert, select, and_, update
from sqlalchemy.exc import SQLAlchemyError

from app.dao.base.base_dao import BaseDao
from app.dao.user.pair_dao import PairDao
from app.dao.wish.wish_dao import WishDao
from app.database import async_session_maker
from app.models.user.models import User
from app.models.wishes.models import Wish, ActiveWish


logger = logging.getLogger("ACTIVE_DAO")


class ActiveDao(BaseDao):
    model = ActiveWish

    @classmethod
    async def create_active_wish(cls, user: User):
        """
        Создает активное желание для пользователя.

        :param user: Объект пользователя.
        """
        async with async_session_maker() as session:
            try:
                partner = await PairDao.get_partner(user)
                wish = await WishDao.get_random_wish_my_partner(user)
                if wish is None:
                    return None
                time = await cls._get_random_time()  # [здесь изменения]
                query = insert(cls.model).values(
                    executor_id=user.id,
                    owner_id=partner.id,
                    wish_id=wish.id,
                    expired_at=time,
                    title=wish.title,
                )
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in create_active_wish: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in create_active_wish: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def _get_random_time(cls) -> datetime:
        """
        Генерирует случайное время истечения для активного желания.

        :return: Случайное время истечения (datetime).
        """
        now = datetime.now()
        dt = timedelta(minutes=random.randint(1000, 5000))
        expired_at = now + dt
        return expired_at

    @classmethod
    async def get_active_wish_by_executor(cls, executor: User) -> ActiveWish or None:
        """
        Получает активное желание, через поле executor.

        :param executor: Объект пользователя (исполнитель).
        :return: Объект ActiveWish или None, если желание не найдено.
        """
        async with async_session_maker() as session:
            try:
                query = select(cls.model).where(and_(
                    cls.model.executor_id == executor.id,
                    ActiveWish.fulfilled.__eq__(False)
                ))
                result = await session.execute(query)
                wish = result.scalars().first()
                return wish

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in get_active_wish_by_executor: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in get_active_wish_by_executor: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def get_wish_from_active_wish(cls, user: User) -> ActiveWish or None:
        """
        Получает желание для текущего пользователя.

        :param user: Объект пользователя.
        :return: Объект ActiveWish или None, если желание не найдено.
        """
        async with async_session_maker() as session:
            try:
                wish = await cls.get_active_wish_by_executor(executor=user)
                if not wish:
                    return None
                query = select(Wish).where(Wish.id == wish.wish_id)
                result = await session.execute(query)
                wish = result.scalars().one_or_none()
                return wish

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in get_wish_from_active_wish: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in get_wish_from_active_wish: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def accept_active_wish(cls, user: User):
        """
        Подтверждает выполнение активного желания для пользователя.

        :param user: Объект пользователя.
        """
        async with async_session_maker() as session:
            try:
                query = update(cls.model).where(cls.model.executor_id == user.id).values(
                    fulfilled=True,
                    fulfilled_at=datetime.now(),
                    description="Выполнил желание"
                )
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in accept_active_wish: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in accept_active_wish: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def reject_active_wish(cls, executor: User):
        """
        Отклоняет активное желание для исполнителя.

        :param executor: Объект пользователя (исполнитель).
        """
        async with async_session_maker() as session:
            try:
                query = update(cls.model).where(cls.model.executor_id == executor.id).values(
                    fulfilled=False,
                    fulfilled_at=datetime.now(),
                    description="Не выполнил желание"
                )
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in reject_active_wish: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in reject_active_wish: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def get_all_unfulfilled_wish(cls) -> list[ActiveWish]:
        """
        Получает все невыполненные желания, срок выполнения которых истек.

        :return: Список объектов ActiveWish.
        """
        async with async_session_maker() as session:
            try:
                query = select(cls.model).where(and_(
                    cls.model.fulfilled.__eq__(False),
                    cls.model.expired_at.__lt__(datetime.now())
                ))
                result = await session.execute(query)
                wishes = result.scalars().all()
                return wishes

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in get_all_unfulfilled_wish: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in get_all_unfulfilled_wish: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def check_active_wish(cls, user: User) -> bool:
        """
        Проверяет наличие активных желаний.

        :param user: Объект пользователя.
        :return: True, если есть активные желания, иначе False.

        """
        async with async_session_maker() as session:
            try:
                if not bool(user):
                    return False
                query = select(cls.model).where(and_(
                    cls.model.executor_id == user.id,
                    cls.model.fulfilled.__eq__(False)
                ))
                result = await session.execute(query)
                wish = result.scalars().first()
                return bool(wish)

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in check_active_wish: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in check_active_wish: {e}")
                raise

            finally:
                await session.close()
