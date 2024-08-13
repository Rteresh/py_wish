import random
from datetime import datetime

from sqlalchemy import insert, select, and_, update

from app.crypto.encryption_manager import EncryptionManager
from app.dao.base.base_dao import BaseDao
from app.dao.user.pair_dao import PairDao
from app.database import async_session_maker
from app.models.user.models import User
from app.models.wishes.models import Wish

encryption_manager = EncryptionManager()


class WishDao(BaseDao):
    model = Wish

    @classmethod
    async def create_wish(cls, text: str, user: User):
        """
        Создает новое желание для пользователя и сохраняет его в базе данных.

        :param text: Текст желания.
        :param user: Объект пользователя, для которого создается желание.
        """
        async with async_session_maker() as session:
            try:
                query = insert(cls.model).values(
                    title=encryption_manager.encrypt(plaintext=text),
                    user_id=user.id
                )
                await session.execute(query)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise RuntimeError(f"Ошибка при создании желания: {e}")

    @classmethod
    async def get_all_wish_by_user(cls, user: User):
        """
        Возвращает все желания пользователя, отсортированные по дате создания.

        :param user: Объект пользователя.
        :return: Список желаний.
        """
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.user_id == user.id).order_by(cls.model.id.desc())
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def get_unfulfilled_wishes_by_user_id(cls, user: User):
        """
        Возвращает все невыполненные желания пользователя.

        :param user: Объект пользователя.
        :return: Список невыполненных желаний.
        """
        async with async_session_maker() as session:
            query = select(cls.model).where(
                and_(
                    cls.model.user_id == user.id,
                    cls.model.fulfilled == False
                )
            )
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def get_wishes_my_partner(cls, user: User):
        """
        Возвращает невыполненные желания партнера пользователя.

        :param user: Объект пользователя.
        :return: Список невыполненных желаний партнера или None, если партнера нет.
        """
        partner = await PairDao.get_my_partner(user)
        if not partner:
            return None
        return await cls.get_unfulfilled_wishes_by_user_id(partner)

    @classmethod
    async def get_random_wish_my_partner(cls, user: User):
        """
        Возвращает случайное невыполненное желание партнера пользователя.

        :param user: Объект пользователя.
        :return: Случайное желание или None, если партнера или желаний нет.
        """
        wishes = await cls.get_wishes_my_partner(user)
        if not wishes:
            return None
        return random.choice(wishes)

    @classmethod
    async def confirm_wish(cls, wish: Wish):
        """
        Подтверждает выполнение желания.

        :param wish: Объект желания.
        """
        async with async_session_maker() as session:
            try:
                query = update(cls.model).where(cls.model.id == wish.id).values(
                    fulfilled=True,
                    fulfilled_at=datetime.now(),
                    description="Выполнил желание"
                )
                await session.execute(query)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise RuntimeError(f"Ошибка при подтверждении выполнения желания: {e}")

    @classmethod
    async def reject_wish(cls, wish: Wish):
        """
        Отклоняет желание, помечая его как невыполненное.

        :param wish: Объект желания.
        """
        async with async_session_maker() as session:
            try:
                query = update(cls.model).where(cls.model.id == wish.id).values(
                    fulfilled=False,
                    fulfilled_at=datetime.now(),
                    description="Не выполнил желание"
                )
                await session.execute(query)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise RuntimeError(f"Ошибка при отклонении желания: {e}")

    @classmethod
    async def update_wish(cls, wish: Wish, text: str):
        """
        Обновляет текст желания.

        :param wish: Объект желания.
        :param text: Новый текст желания.
        """
        async with async_session_maker() as session:
            try:
                query = update(cls.model).where(cls.model.id == wish.id).values(
                    title=encryption_manager.encrypt(text)
                )
                await session.execute(query)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise RuntimeError(f"Ошибка при обновлении желания: {e}")
