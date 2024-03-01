from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


# ГЛАВНОЕ МЕНЮ СУПЕРАДМИН
def keyboards_superadmin():
    logging.info("keyboards_superadmin")
    button_1 = KeyboardButton(text='Получить ключ')
    # button_2 = KeyboardButton(text='Статистика')
    button_3 = KeyboardButton(text='Отчет по продажам')
    button_4 = KeyboardButton(text='Менеджер')
    button_5 = KeyboardButton(text='Остаток')
    button_6 = KeyboardButton(text='Администраторы')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_3], [button_4], [button_5], [button_6]],
        resize_keyboard=True
    )
    return keyboard


# ГЛАВНОЕ МЕНЮ МЕНЕДЖЕРА
def keyboards_manager():
    logging.info("keyboards_superadmin")
    button_1 = KeyboardButton(text='Получить ключ')
    # button_2 = KeyboardButton(text='Статистика')
    button_3 = KeyboardButton(text='Отчет по продажам')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_3]],
        resize_keyboard=True
    )
    return keyboard

def keyboard_question(telegram_id) -> None:
    """
    ПОЛЬЗОВАТЕЛЬ -> Удалить -> подтверждение удаления пользователя из базы
    :return:
    """
    logging.info("keyboard_set_user_operator")
    button_1 = InlineKeyboardButton(text='Да',  callback_data=f'yes_{telegram_id}')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1]],
    )
    return keyboard