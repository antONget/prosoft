from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboard_main_leave() -> InlineKeyboardMarkup:
    logging.info("keyboard_select_scale_sales")
    button_1 = InlineKeyboardButton(text='Выбрать отпуск', callback_data=f'personal_leave')
    button_2 = InlineKeyboardButton(text='Посмотреть отпуск', callback_data=f'show_leave')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1],[button_2]], )
    return keyboard


def keyboard_send_admin() -> InlineKeyboardMarkup:
    logging.info("keyboard_select_scale_sales")
    button_1 = InlineKeyboardButton(text='Согласовать отпуск', callback_data=f'sendadmin')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1],], )
    return keyboard


def keyboard_confirm_admin_leave(telegram_id: int) -> InlineKeyboardMarkup:
    logging.info("keyboard_confirm_admin_leave")
    button_1 = InlineKeyboardButton(text='Подтвердить', callback_data=f'adminleave_confirm_{telegram_id}')
    button_2 = InlineKeyboardButton(text='Отклонить', callback_data=f'adminleave_cancel_{telegram_id}')
    button_3 = InlineKeyboardButton(text='Другой срок', callback_data=f'adminleave_other_{telegram_id}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3]], )
    return keyboard


def keyboard_send_change_leave(id_manager, change_leave, id_admin) -> InlineKeyboardMarkup:
    logging.info("keyboard_select_scale_sales")
    button_1 = InlineKeyboardButton(text='Отправить', callback_data=f'sendchangeleave_{id_manager}_{change_leave}_{id_admin}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1],], )
    return keyboard


def keyboard_send_change_leave_confirm(id_manager, change_leave, id_admin) -> InlineKeyboardMarkup:
    logging.info("keyboard_select_scale_sales")
    button_1 = InlineKeyboardButton(text='Cогласиться', callback_data=f'sendchangeleaveconfirm_{id_manager}_{change_leave}_{id_admin}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1],], )
    return keyboard