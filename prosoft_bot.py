import asyncio
import logging

from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from handlers import admin_main_handlers, admin_manager_handlers, admin_rest_keys, manager_statistic_handlers, \
    admin_edit_admin_list
from handlers import user_auth_handler, manager_keys_handlers, manager_sales
from handlers import other_handlers
from handlers.admin_rest_keys import process_sheduler
from handlers.manager_sales import process_sendler_stat_scheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from middlewares.outer import Middleware_message, Middleware_callback
from handlers.manager_keys_handlers import router as router_user
from handlers.manager_sales import router as router_sales
# Инициализируем logger
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        filename="py_log.log",
        filemode='w',
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(process_sheduler, 'cron', hour=20, minute=0, second=0, args=(bot,))
    scheduler.add_job(process_sendler_stat_scheduler, 'cron', hour=0, minute=0, second=0, args=(bot,))
    scheduler.start()
    # Регистрируем router в диспетчере
    dp.include_router(admin_main_handlers.router)
    dp.include_router(admin_manager_handlers.router)
    dp.include_router(admin_rest_keys.router)
    dp.include_router(admin_edit_admin_list.router)
    dp.include_router(manager_statistic_handlers.router)
    dp.include_router(manager_keys_handlers.router)
    dp.include_router(manager_sales.router)
    dp.include_router(user_auth_handler.router)
    dp.include_router(other_handlers.router)

    router_user.message.middleware(Middleware_message())
    router_user.callback_query.middleware(Middleware_callback())
    router_sales.message.middleware(Middleware_message())
    router_sales.callback_query.middleware(Middleware_callback())
    # Пропускаем накопившиеся update и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
