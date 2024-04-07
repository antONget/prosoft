from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import logging


# ГЛАВНОЕ МЕНЮ СУПЕРАДМИН
def keyboards_super_admin() -> ReplyKeyboardMarkup:
    logging.info("keyboards_super_admin")
    button_1 = KeyboardButton(text='Получить ключ')
    button_3 = KeyboardButton(text='Отчет по продажам')
    button_4 = KeyboardButton(text='Менеджер')
    button_5 = KeyboardButton(text='Остаток')
    button_6 = KeyboardButton(text='Администраторы')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_3], [button_4], [button_5], [button_6]],
        resize_keyboard=True
    )
    return keyboard


def keyboards_super_admin_v1() -> ReplyKeyboardMarkup:
    logging.info("keyboards_super_admin_new")
    button_1 = KeyboardButton(text='Ключ')
    button_2 = KeyboardButton(text='Отчет')
    button_3 = KeyboardButton(text='Персонал')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_2], [button_3]],
        resize_keyboard=True
    )
    return keyboard


# ГЛАВНОЕ МЕНЮ МЕНЕДЖЕРА
def keyboards_manager() -> ReplyKeyboardMarkup:
    logging.info("keyboards_manager")
    button_1 = KeyboardButton(text='Получить ключ')
    button_3 = KeyboardButton(text='Отчет по продажам')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_3]],
        resize_keyboard=True
    )
    return keyboard


def keyboards_manager_v1() -> ReplyKeyboardMarkup:
    logging.info("keyboards_manager_new")
    button_1 = KeyboardButton(text='Ключ')
    button_2 = KeyboardButton(text='Отчет')
    button_3 = KeyboardButton(text='Персонал')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_2], [button_3]],
        resize_keyboard=True
    )
    return keyboard


def keyboard_personal_admin() -> InlineKeyboardMarkup:
    logging.info("keyboard_report_admin")
    button_1 = InlineKeyboardButton(text='Смены', callback_data='personal_work')
    button_2 = InlineKeyboardButton(text='Отпуск', callback_data='personal_leave')
    button_3 = InlineKeyboardButton(text='Менеджер', callback_data='personal_manager')
    button_4 = InlineKeyboardButton(text='Администратор', callback_data='personal_admin')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_4]],)
    return keyboard


def keyboard_personal_manager() -> InlineKeyboardMarkup:
    logging.info("keyboard_report_manager")
    button_1 = InlineKeyboardButton(text='Смены', callback_data='personal_work')
    button_2 = InlineKeyboardButton(text='Отпуск', callback_data='personal_leave')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]],)
    return keyboard
