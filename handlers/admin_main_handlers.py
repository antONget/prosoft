import logging

from aiogram import Router, Bot
from aiogram.filters import CommandStart, or_f
from aiogram.types import Message
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
from filter.admin_filter import chek_admin,chek_admin_1
from filter.user_filter import check_user
from module.data_base import create_table_users, add_super_admin

from keyboards.keyboards_admin import keyboards_superadmin, keyboards_manager
import requests
from config_data.config import Config, load_config

router = Router()
config: Config = load_config()


def get_telegram_user(user_id, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    # print(response.json())
    return response.json()


@router.message(CommandStart(), or_f(lambda message: chek_admin(message.chat.id),
                lambda message: chek_admin_1(message.chat.id)))
async def process_start_command_superadmin(message: Message, bot: Bot) -> None:
    logging.info("process_start_command")
    """
    Запуск бота администратором
    :param message: 
    :return: 
    """
    create_table_users()
    add_super_admin(id_admin=message.chat.id, user_name=message.from_user.username)
    # await message.answer_sticker(sticker='CAACAgIAAxkBAAMGZdsqEf4QhJm2JYtIy9KrTYs8aBUAAtY8AAIbsthKlKy5IzD6RCM0BA')
    await message.answer(text=f"Привет, {message.from_user.first_name} 👋\n"
                              f"Здесь можно оформить заказ на ключи, оформить замену на ключи,"
                              f" получить отчёты менеджера.",
                         reply_markup=keyboards_superadmin())


@router.message(CommandStart(), lambda message: check_user(message.chat.id))
async def process_start_command_admin(message: Message) -> None:
    logging.info("process_start_command_admin")
    """
    Запуск бота администратором
    :param message: 
    :return: 
    """
    create_table_users()
    # CAACAgIAAxkBAAMGZdsqEf4QhJm2JYtIy9KrTYs8aBUAAtY8AAIbsthKlKy5IzD6RCM0BA
    # await message.answer(text="Вы менеджер проекта",
    #                      reply_markup=keyboards_manager())
    await message.answer_sticker(sticker='CAACAgIAAxkBAAMGZdsqEf4QhJm2JYtIy9KrTYs8aBUAAtY8AAIbsthKlKy5IzD6RCM0BA')
    await message.answer(text=f"Привет, {message.from_user.first_name} 👋\n"
                              f"Здесь можно оформить заказ на ключи, оформить замену на ключи,"
                              f" получить отчёты менеджера.",
                         reply_markup=keyboards_manager())
