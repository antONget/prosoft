from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboard_select_period() -> None:
    """
    СТАТИСТИКА - [День][Неделя][Месяц]
    :return:
    """
    logging.info("keyboard_edit_list_user")
    button_1 = InlineKeyboardButton(text='День', callback_data='period_1')
    button_2 = InlineKeyboardButton(text='Неделя', callback_data='period_7')
    button_3 = InlineKeyboardButton(text='Месяц', callback_data='period_30')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3]],)
    return keyboard


def keyboard_select_scale() -> None:
    """
    СТАТИСТИКА -
    :return:
    """
    logging.info("keyboard_select_category_keys")
    button_1 = InlineKeyboardButton(text='Менеджер', callback_data='manager')
    button_2 = InlineKeyboardButton(text='Компания', callback_data='company')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]],)
    return keyboard


def keyboards_list_product(list_manager: list):
    logging.info("keyboards_list_product")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for i, manager in enumerate(list_manager):
        callback = f'manager_{manager[1]}'
        print(callback)
        buttons.append(InlineKeyboardButton(
            text=manager[1],
            callback_data=callback))
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()

