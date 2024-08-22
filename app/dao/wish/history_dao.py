import logging

from sqlalchemy import insert, select
from sqlalchemy.exc import SQLAlchemyError

from app.dao.base.base_dao import BaseDao
from app.database import async_session_maker
from app.models.user.models import User
from app.models.wishes.models import WishHistory

logger = logging.getLogger('HISTORY_DAO')


class HistoryDao(BaseDao):
    model = WishHistory

    @classmethod
    async def create_wish_history(cls, active_wish):
        async with async_session_maker() as session:
            try:
                title = active_wish.title
                owner_id = active_wish.owner_id
                executor = active_wish.executor_id
                fulfilled = active_wish.fulfilled

                query = insert(cls.model).values(
                    title=title,
                    owner_id=owner_id,
                    executor_id=executor,
                    fulfilled=fulfilled,
                )

                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in create_wish_history: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in create_wish_history: {e}")
                raise
            finally:
                await session.close()

    @classmethod
    async def get_all_wish_history_by_owner(cls, user: User):
        async with async_session_maker() as session:
            try:
                query = select(cls.model).where(cls.model.owner_id == user.id)
                result = await session.execute(query)
                wishes = result.scalars().all()
                return wishes

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in get_all_wish_history_by_owner: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in get_all_wish_history_by_owner: {e}")
                raise
            finally:
                await session.close()

    @classmethod
    async def get_all_active_wish_history_by_executor(cls, user: User):
        async with async_session_maker() as session:
            try:
                query = select(cls.model).where(cls.model.executor_id == user.id)
                result = await session.execute(query)
                wishes = result.scalars().all()
                return wishes

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in get_all_active_wish_history_by_executor: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in get_all_active_wish_history_by_executor: {e}")
                raise
            finally:
                await session.close()

    @classmethod
    async def get_all_wish_history(cls):
        async with async_session_maker() as session:
            try:
                query = select(cls.model)
                result = await session.execute(query)
                wishes = result.scalars()
                return wishes

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred in get_all_wish_history: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred in get_all_wish_history: {e}")
                raise
            finally:
                await session.close()
