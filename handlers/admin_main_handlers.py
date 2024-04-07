from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from filter.admin_filter import check_admin
from filter.user_filter import check_user
from module.data_base import create_table_users, add_super_admin
from keyboards.keyboards_admin import keyboards_super_admin_v1, keyboards_manager_v1, keyboard_personal_admin, \
    keyboard_personal_manager
from keyboards.keyboard_sales import keyboard_report_admin, keyboard_report_manager
from config_data.config import Config, load_config

import requests
import logging

router = Router()
config: Config = load_config()


def get_telegram_user(user_id, bot_token):
    """
    Проверка того что бот знает пользователя
    :param user_id:
    :param bot_token:
    :return:
    """
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    return response.json()


@router.message(CommandStart(), lambda message: check_admin(message.chat.id))
async def process_start_command_admin(message: Message) -> None:
    logging.info("process_start_command")
    """
    Запуск бота администратором
    :param message: 
    :return: 
    """
    create_table_users()
    add_super_admin(id_admin=message.chat.id, user_name=message.from_user.username)
    # стикер для приветственного сообщения для бота @PROSOFT_ManagerBot, снять комментарий при пушинге
    # await message.answer_sticker(sticker='CAACAgIAAxkBAAMGZdsqEf4QhJm2JYtIy9KrTYs8aBUAAtY8AAIbsthKlKy5IzD6RCM0BA')
    await message.answer(text=f"Привет, {message.from_user.first_name} 👋\n"
                              f"Здесь можно оформить заказ на ключи, оформить замену на ключи,"
                              f" получить отчёты менеджера.",
                         reply_markup=keyboards_super_admin_v1())


@router.message(CommandStart(), lambda message: check_user(message.chat.id))
async def process_start_command_manager(message: Message) -> None:
    logging.info("process_start_command_manager")
    """
    Запуск бота менеджером
    :param message: 
    :return: 
    """
    create_table_users()
    # стикер для приветственного сообщения для бота @PROSOFT_ManagerBot, снять комментарий при пушинге
    # await message.answer_sticker(sticker='CAACAgIAAxkBAAMGZdsqEf4QhJm2JYtIy9KrTYs8aBUAAtY8AAIbsthKlKy5IzD6RCM0BA')
    await message.answer(text=f"Привет, {message.from_user.first_name} 👋\n"
                              f"Здесь можно оформить заказ на ключи, оформить замену на ключи,"
                              f" получить отчёты менеджера.",
                         reply_markup=keyboards_manager_v1())


@router.message(F.text == 'Персонал')
async def process_personal(message: Message) -> None:
    logging.info(f'process_personal: {message.chat.id}')
    if check_admin(telegram_id=message.chat.id):
        await message.answer(text="Выберите требуемый раздел",
                             reply_markup=keyboard_personal_admin())


@router.message(F.text == 'График')
async def process_personal(message: Message) -> None:
    logging.info(f'process_personal: {message.chat.id}')
    if check_user(telegram_id=message.chat.id):
        await message.answer(text="Выберите требуемый раздел",
                             reply_markup=keyboard_personal_manager())


@router.message(F.text == 'Отчет')
async def process_get_report(message: Message) -> None:
    """
    Начало цепочки сообщений для выбора:
    1. отчета о продажах (выбор периода для которого выдается отчет о продажах)
    Администратор - может выбрать отчет за менеджера или компанию
    Менеджер - может посмотреть отчеты только за менеджеров
    2. отчета о заменах по аналогии с отчетом о продажах
    3. отчет об остатках ключей (доступен только админу)
    :param message:
    :return:
    """
    logging.info(f'process_get_report: {message.chat.id}')
    if check_admin(telegram_id=message.chat.id):
        await message.answer(text="Отчет по какому разделу требуется?",
                             reply_markup=keyboard_report_admin())
    elif check_user(telegram_id=message.chat.id):
        await message.answer(text="Отчет по какому разделу требуется?",
                             reply_markup=keyboard_report_manager())