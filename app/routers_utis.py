from aiogram import Router

from app.routers.base.base_router import base_router
from app.routers.menu.keyboard_utils import keyboard1
from app.routers.menu.language_router import language_router
from app.routers.menu.menu_router import menu_router
from app.routers.menu.test import test_router
from app.routers.user.pair_router import pair_router
from app.routers.user.user_router import user_router
from app.routers.wish.active_wish_router import active_router
from app.routers.wish.wish_routers import wish_router


def get_routers():
    main_router = Router()
    main_router.include_router(user_router)
    main_router.include_router(base_router)
    main_router.include_router(wish_router)
    main_router.include_router(pair_router)
    main_router.include_router(menu_router)
    main_router.include_router(active_router)
    main_router.include_router(test_router)
    main_router.include_router(language_router)
    main_router.include_router(keyboard1)
    return main_router
