from typing import Dict, Any

from aiogram import types
from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18nMiddleware

from app.dao.user.user_dao import UserDao


class MyI18nMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        if isinstance(event, types.Message):
            user_id = event.from_user.id
        elif isinstance(event, types.CallbackQuery):
            user_id = event.from_user.id
        else:
            return self.i18n.default_locale

        user = await UserDao.find_one_or_none(id=user_id)
        return user.language if user and user.language else self.i18n.default_locale
