from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboard_select_period_change_key() -> InlineKeyboardMarkup:
    logging.info("keyboard_select_period_change_key")
    button_1 = InlineKeyboardButton(text='Сегодня', callback_data='changeperiod_1')
    button_2 = InlineKeyboardButton(text='Календарь', callback_data='changeperiod_calendar')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]],)
    return keyboard


def keyboard_select_scale_change_key() -> InlineKeyboardMarkup:
    logging.info("keyboard_select_scale_change_key")
    button_1 = InlineKeyboardButton(text='Менеджер', callback_data='changemanager')
    button_2 = InlineKeyboardButton(text='Компания', callback_data='changecompany')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]],)
    return keyboard


def keyboards_list_product_change_key(list_manager: list):
    logging.info("keyboards_list_product_change_key")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for i, manager in enumerate(list_manager):
        callback = f'changemanager#{manager[1]}'
        buttons.append(InlineKeyboardButton(
            text=manager[1],
            callback_data=callback))
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()