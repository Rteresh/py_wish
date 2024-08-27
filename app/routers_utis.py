from aiogram import Router

# Импорт роутеров
from app.routers.base.base_router import base_router
from app.routers.menu.language_router import language_router
from app.routers.menu.faq_router import menu_router
from app.routers.user.pair_router import pair_router
from app.routers.user.user_router import user_router
from app.routers.wish.active_wish_router import active_router
from app.routers.wish.history_router import history_router
from app.routers.wish.wish_router import wish_router
from app.routers.promo.promo_routers import promo_router

# Импорт клавиатурных роутеров
from app.routers.menu.keyboard.help_utils_menu import help_keyboard
from app.routers.menu.keyboard.histroy_utils_menu import history_keyboard
from app.routers.menu.keyboard.main_keyboard_utils_menu import main_keyboard
from app.routers.menu.keyboard.pair_utils_menu import pair_keyboard
from app.routers.menu.keyboard.start_utils_menu import start_keyboard
from app.routers.menu.keyboard.wish_utils_menu import wish_keyboard
from app.routers.menu.keyboard.settings_utils_menu import settings_keyboard


def get_routers() -> Router:
    """
    Создает и возвращает главный роутер, который включает в себя все дочерние роутеры и клавиатурные роутеры приложения.

    Главный роутер объединяет все маршруты, определенные в приложении, для централизованного управления.

    :return: Объект главного роутера с включенными дочерними роутерами и клавиатурами.
    """
    # Создание главного роутера
    main_router = Router()

    main_router.include_router(user_router)
    main_router.include_router(base_router)
    main_router.include_router(wish_router)
    main_router.include_router(pair_router)
    main_router.include_router(menu_router)
    main_router.include_router(active_router)
    main_router.include_router(language_router)
    main_router.include_router(promo_router)

    # Подключение клавиатурных роутеров
    main_router.include_router(main_keyboard)
    main_router.include_router(wish_keyboard)
    main_router.include_router(pair_keyboard)
    main_router.include_router(help_keyboard)
    main_router.include_router(history_router)
    main_router.include_router(history_keyboard)
    main_router.include_router(start_keyboard)
    main_router.include_router(settings_keyboard)

    return main_router
