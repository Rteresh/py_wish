from aiogram import Bot
from aiogram.utils.i18n import gettext as _
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.crypto.encryption_manager import decrypt as d
from app.dao.user.pair_dao import PairDao
from app.dao.user.user_dao import UserDao
from app.dao.wish.active_wish_dao import ActiveDao
from app.routers.utils import reject_wish

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')


async def alert_timeout_active(bot: Bot):
    """
    Обрабатывает невыполненные желания и отправляет уведомления пользователям.

    Args:
        bot (Bot): Экземпляр бота для отправки сообщений.
    """
    active_wishes = await ActiveDao.get_all_unfulfilled_wish()
    for active_wish in active_wishes:
        owner = await UserDao.find_one_or_none(id=active_wish.owner_id)
        executor = await UserDao.find_one_or_none(id=active_wish.executor_id)

        await bot.send_message(
            owner.id,
            _("Ваше желание {title} не выполнено,\n партнером: {executor}.").format(
                title=d(active_wish.title),
                executor=executor.name
            )
        )

        await bot.send_message(
            executor.id,
            _("Желание {title} партнера {partner} вы не выполнили").format(
                title=d(active_wish.title),
                partner=owner.username
            )
        )

        # Обновление в бд
        await reject_wish(
            active_wish=active_wish,
            user=executor
        )


async def alert_pair_request():
    """
    Удаляет просроченные запросы на создание пар в базе данных.
    """
    await PairDao.delete_timeout_pair_request()


async def scheduler_run(bot: Bot):
    """
    Запускает планировщик задач для периодического выполнения уведомлений и очистки просроченных запросов.

    Args:
        bot (Bot): Экземпляр бота для передачи в задачи планировщика.
    """
    scheduler.add_job(alert_timeout_active, 'interval', minutes=1, args=[bot])
    scheduler.add_job(alert_pair_request, 'interval', minutes=1)
    scheduler.start()
