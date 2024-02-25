from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboard_select_period_sales() -> None:
    logging.info("keyboard_select_period_sales")
    button_1 = InlineKeyboardButton(text='День', callback_data='salesperiod_1')
    button_2 = InlineKeyboardButton(text='Неделя', callback_data='salesperiod_7')
    button_3 = InlineKeyboardButton(text='Месяц', callback_data='salesperiod_30')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3]],)
    return keyboard


def keyboard_select_scale_sales() -> None:
    logging.info("keyboard_select_scale_sales")
    button_1 = InlineKeyboardButton(text='Менеджер', callback_data='salesmanager')
    button_2 = InlineKeyboardButton(text='Компания', callback_data='salescompany')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]],)
    return keyboard


def keyboards_list_product_sales(list_manager: list):
    logging.info("keyboards_list_product_sales")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for i, manager in enumerate(list_manager):
        callback = f'salesmanager#{manager[1]}'
        print(callback)
        buttons.append(InlineKeyboardButton(
            text=manager[1],
            callback_data=callback))
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()

