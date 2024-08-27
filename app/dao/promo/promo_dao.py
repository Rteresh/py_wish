import logging
from datetime import datetime

from sqlalchemy import insert, select, update
from sqlalchemy.exc import SQLAlchemyError

from app.config import setup_logging  # noqa
from app.dao.base.base_dao import BaseDao
from app.database import async_session_maker
from app.models.promo.models import Promo

logger = logging.getLogger("PROMO_DAO")


class PromoDao(BaseDao):
    model = Promo

    @classmethod
    async def create_promo(cls, code: str, duration: int) -> None:
        """
        Метод создает новую запись промо кода в базе данных.
        :param duration: Длительность действия премиум аккаунта в месяцах.
        :param code: Название промо кода.
        """
        async with async_session_maker() as session:
            try:
                query = insert(cls.model).values(
                    code=code,
                    duration=duration
                )
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in create_promo: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred while creating promo: {e}")
                raise

    @classmethod
    async def get_promo_by_code(cls, code: str) -> Promo or None:
        """
        Метод возвращает промо код по его названию.
        Args:
            code: Название промо кода.

        Returns:
            Promo: Промокод или None.
        """
        async with async_session_maker() as session:
            try:
                query = select(cls.model).where(cls.model.code == code)
                result = await session.execute(query)
                promo = result.scalar_one_or_none()
                return promo

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in get_promo_by_code: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred while getting promo: {e}")
                raise

    @classmethod
    async def get_finished_promo(cls) -> list:
        """
        Метод возвращает все промо коды, которые уже закончили свое действие.
        """
        async with async_session_maker() as session:
            try:
                query = select(cls.model).where(cls.model.is_active.__eq__(False))
                result = await session.execute(query)
                promos = result.scalars().all()
                return promos

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in get_finished_promo: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred while getting finished promo: {e}")
                raise

    @classmethod
    async def get_finished_time_promo(cls) -> list:
        """
        Метод возвращает все промо коды, которые уже закончили свое действие.
        :return: promos
        """
        async with async_session_maker() as session:
            try:
                query = select(cls.model).where(cls.model.finished_at < datetime.utcnow())
                result = await session.execute(query)
                promos = result.scalars().all()
                return promos

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in get_finished_time_promo: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred while getting finished time promo: {e}")
                raise

    @classmethod
    async def set_finished(cls, promo: Promo) -> None:
        """
        Метод устанавливает флаг is_active в False для промо кода.
        Args:
            :param promo: Promo модель
        """
        async with async_session_maker() as session:
            try:
                query = update(cls.model).where(cls.model.id == promo.id).values(is_active=False)
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in set_finished: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred while setting promo finished: {e}")
                raise

    @classmethod
    async def set_all_finished(cls):
        """
        Метод завершает все промо коды, которые уже закончили свое действие.
        :return:
        """
        proms = await cls.get_finished_time_promo()

        for promo in proms:
            await cls.set_finished(promo)

