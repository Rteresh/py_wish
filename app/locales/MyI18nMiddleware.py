from abc import ABC

from aiogram.types import Message
from aiogram.utils.i18n import I18nMiddleware

from app.dao.user.user_dao import UserDao


class MyI18nMiddleware(I18nMiddleware, ABC):

    @staticmethod
    async def get_user_locale(args: list[Message, dict[str]]):
        user_id = args['user'].id
        user = await UserDao.find_one_or_none(id=user_id)
        return user.language
