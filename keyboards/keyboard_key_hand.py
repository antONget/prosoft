from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboard_select_category_handkeys() -> None:
    """
    КЛЮЧ - [Ручной ввод] - Категории
    :return:
    """
    logging.info("keyboard_select_category_keys")
    button_1 = InlineKeyboardButton(text='Ключ Office', callback_data='handgetproduct_office')
    button_2 = InlineKeyboardButton(text='Ключ Windows', callback_data='handgetproduct_windows')
    button_3 = InlineKeyboardButton(text='Ключ Server', callback_data='handgetproduct_server')
    button_4 = InlineKeyboardButton(text='Ключ Visio', callback_data='handgetproduct_visio')
    button_5 = InlineKeyboardButton(text='Ключ Project', callback_data='handgetproduct_project')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_4], [button_5]],)
    return keyboard


def keyboard_select_office_handkeys() -> None:
    """
    КЛЮЧ - [Ручной ввод] - Категории - Office
    :return:
    """
    logging.info("keyboard_select_office_handkeys")
    button_1 = InlineKeyboardButton(text='Ключ Office 365 (Персональный)', callback_data='handgetkey#Office 365 (Персональный)')
    button_2 = InlineKeyboardButton(text='Ключ Office 365 (Семейный)', callback_data='handgetkey#Office 365 (Семейный)')
    button_3 = InlineKeyboardButton(text='С привязкой Office 2021 для (Windows)', callback_data='handgetkey#Office 2021 для (Windows)')
    button_4 = InlineKeyboardButton(text='С привязкой Office 2019 для (Windows)', callback_data='handgetkey#Office 2019 для (Windows)')
    button_5 = InlineKeyboardButton(text='С привязкой Office 2016 для (Windows)', callback_data='handgetkey#Office 2016 для (Windows)')
    button_6 = InlineKeyboardButton(text='С привязкой Office 2021 для (MacOS)', callback_data='handgetkey#Office 2021 для (MacOS)')
    button_7 = InlineKeyboardButton(text='С привязкой Office 2019 для (MacOS)', callback_data='handgetkey#Office 2019 для (MacOS)')
    button_8 = InlineKeyboardButton(text='С привязкой Office 2016 для (MacOS)', callback_data='handgetkey#Office 2016 для (MacOS)')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_4], [button_5],
                                                     [button_6], [button_7], [button_8]],)
    return keyboard



def keyboard_select_windows_handkeys() -> None:
    """
    КЛЮЧ - [Ручной ввод] - Категории - Windows
    :return:
    """
    logging.info("keyboard_select_office_handkeys")
    button_1 = InlineKeyboardButton(text='Windows 8.1 Pro', callback_data='handgetkey#Windows 8.1 Pro')
    button_2 = InlineKeyboardButton(text='Windows 10/11 Workstation', callback_data='handgetkey#Windows 10/11 Workstation')
    button_3 = InlineKeyboardButton(text='Windows 10/11 Корпоративная', callback_data='handgetkey#Windows 10/11 Корпоративная')
    button_4 = InlineKeyboardButton(text='Windows 10/11 Корпоративная 2016', callback_data='handgetkey#Windows 10/11 Корпоративная 2016')
    button_5 = InlineKeyboardButton(text='Windows 10/11 Корпоративная LTSC 2021', callback_data='handgetkey#Windows 10/11 Корпоративная LTSC 2021')
    button_6 = InlineKeyboardButton(text='Windows 10/11 Корпоративная LTSC 2019', callback_data='handgetkey#Windows 10/11 Корпоративная LTSC 2019')
    button_7 = InlineKeyboardButton(text="USB флешка Windows 10/11", callback_data='handgetkey#USB флешка Windows 10/11')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_4], [button_5],
                                                     [button_6], [button_7]],)
    return keyboard


def keyboard_select_server_handkeys() -> None:
    """
    КЛЮЧ - [Ручной ввод] - Категории - Server
    :return:
    """
    logging.info("keyboard_select_office_handkeys")
    button_1 = InlineKeyboardButton(text='Windows Server 2022 Datacenter / Standard', callback_data='handgetkey#Windows Server 2022')
    button_2 = InlineKeyboardButton(text='Windows Server 2019 Datacenter / Standard', callback_data='handgetkey#Windows Server 2019')
    button_3 = InlineKeyboardButton(text='Windows Server 2016 Datacenter / Standard', callback_data='handgetkey#Windows Server 2016')
    button_4 = InlineKeyboardButton(text='Windows Server 2012 Datacenter / Standard', callback_data='handgetkey#Windows Server 2012')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_4]],)
    return keyboard


def keyboard_select_visio_handkeys() -> None:
    """
    КЛЮЧ - [Ручной ввод] - Категории - Visio
    :return:
    """
    logging.info("keyboard_select_office_handkeys")
    button_1 = InlineKeyboardButton(text='С привязкой Visio 2019 Pro', callback_data='handgetkey#С привязкой Visio 2019 Pro')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard


def keyboard_select_project_handkeys() -> None:
    """
    КЛЮЧ - [Ручной ввод] - Категории - Project
    :return:
    """
    logging.info("keyboard_select_project_handkeys")
    button_1 = InlineKeyboardButton(text='Project 2019 Pro', callback_data='handgetkey#Project 2019 Pro')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard


def keyboard_cancel_hand_key() -> None:
    """
    КЛЮЧ - [Ручной ввод] - Категории - Project - отмена добавления ключа
    :return:
    """
    logging.info("keyboard_cancel_hand_key")
    button_1 = InlineKeyboardButton(text='Отмена', callback_data='cancel_hand_key')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard