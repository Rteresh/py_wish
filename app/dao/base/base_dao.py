import logging
from typing import List

from sqlalchemy import select, insert, delete
from sqlalchemy.exc import SQLAlchemyError

from app.database import async_session_maker

logger = logging.getLogger("BASE_DAO")


class BaseDao:
    model = None

    @classmethod
    async def data_all(cls) -> List[dict]:
        """
        Метод data_all возвращает все записи из базы данных для модели, связанной с текущим DAO.

        Returns:
            List[dict]: Список словарей, представляющих записи из базы данных.
        """
        async with async_session_maker() as session:
            try:
                model = await session.execute(select(cls.model.__table__.columns))
                return model.mappings().all()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred data_all: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred data_all: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def find_all(cls, **filter_by):
        """
        Метод find_all возвращает все записи, соответствующие заданным фильтрам.

        Args:
            **filter_by: Ключевые аргументы для фильтрации записей.

        Returns:
            List[dict]: Список словарей, представляющих найденные записи.
        """
        async with async_session_maker() as session:
            try:
                # Убедимся, что модель установлена
                if not cls.model:
                    raise ValueError("Model is not set for DAO")

                query = select(cls.model).filter_by(**filter_by)
                result = await session.execute(query)
                return result.scalars().all()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred find_all: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred find_all: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def find_one_or_none(cls, **filter_by) -> dict or None:
        """
        Метод find_one_or_none возвращает одну запись, соответствующую заданным фильтрам, или None,
         если ничего не найдено.

        Args:
            **filter_by: Ключевые аргументы для фильтрации записей.

        Returns:
            dict or None: Словарь, представляющий найденную запись, или None.
        """
        async with async_session_maker() as session:
            try:
                query = select(cls.model.__table__.columns).filter_by(**filter_by)
                result = await session.execute(query)
                return result.mappings().one_or_none()
            except SQLAlchemyError as e:
                logger.error(f"Database error occurred find_one_or_none: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred find_one_or_none: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def find_by_id(cls, model_id: int) -> dict or None:
        """
        Метод find_by_id возвращает запись по её идентификатору.

        Args:
            model_id: Идентификатор записи.

        Returns:
            dict or None: Словарь, представляющий найденную запись, или None.
        """
        async with async_session_maker() as session:
            try:
                query = select(cls.model.__table__.columns).filter_by(id=model_id)
                result = await session.execute(query)
                return result.mappings().one_or_none()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred find_by_id: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred find_by_id: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def find_by_ids(cls, user_ids: List[int]) -> List[dict]:
        """
        Метод find_by_ids возвращает записи по списку их идентификаторов.

        Args:
            user_ids: Список идентификаторов записей.

        Returns:
            List[dict]: Список словарей, представляющих найденные записи.
        """
        async with async_session_maker() as session:
            try:
                query = select(cls.model).filter(cls.model.id.in_(user_ids))
                result = await session.execute(query)
                return result.scalars().all()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred find_by_ids: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred find_by_ids: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def insert_data(cls, **data):
        """
        Метод insert_data используется для вставки данных в базу данных.

        Args:
            **data: Данные для вставки.

        Returns:
            None
        """
        async with async_session_maker() as session:
            try:
                query = insert(cls.model).values(**data)
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred insert_data: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred insert_data: {e}")
                raise

            finally:
                await session.close()

    # @classmethod
    # async def delete_all(cls):
    #     """
    #     Метод delete_all удаляет все записи из таблицы, связанной с текущим DAO.
    #
    #     Returns:
    #         None
    #     # """
    #     async with async_session_maker() as session:
    #         query = delete(cls.model)__table__.delete
    #         await session.execute(query)
    #         await session.commit()
    #     pass

    @classmethod
    async def delete_all_except_ids(cls, user_ids_to_keep: List[int]):
        """
        Метод delete_all_except_ids удаляет все записи, кроме тех, чьи идентификаторы указаны в списке.

        Args:
            user_ids_to_keep: Список идентификаторов записей, которые необходимо оставить.

        Returns:
            None
        """
        async with async_session_maker() as session:
            try:
                query = delete(cls.model).where(~cls.model.id.in_(user_ids_to_keep))
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred delete_all_except_ids: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred delete_all_except_ids: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def delete_by_ids(cls, user_ids_to_delete: List[int]):
        """
        Метод delete_by_ids удаляет записи по их идентификаторам.

        Args:
            user_ids_to_delete: Список идентификаторов записей, которые необходимо удалить.

        Returns:
            None
        """
        async with async_session_maker() as session:
            try:
                query = delete(cls.model).where(cls.model.id.in_(user_ids_to_delete))
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred delete_by_ids: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred delete_by_ids: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def delete_by_id(cls, model_id: int):
        """
        Метод delete_by_id удаляет запись по её идентификатору.

        Args:
            model_id: Идентификатор записи, которую необходимо удалить.

        Returns:
            None
        """
        async with async_session_maker() as session:
            try:
                query = delete(cls.model).where(cls.model.id == model_id)
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred delete_by_id: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred delete_by_id: {e}")
                raise

            finally:
                await session.close()

    @classmethod
    async def add(cls, **data):
        """
        Метод add используется для добавления новой записи в базу данных.

        Args:
            **data: Данные для вставки.

        Returns:
            None
        """
        async with async_session_maker() as session:
            try:
                query = insert(cls.model).values(**data)
                await session.execute(query)
                await session.commit()

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred add: {e}")
                raise

            except Exception as e:
                logger.error(f"An unexpected error occurred add: {e}")
                raise
            finally:
                await session.close()







