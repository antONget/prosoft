from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboard_select_type_keys() -> None:
    """
    КЛЮЧ - [Выдать][Заменить]
    :return:
    """
    logging.info("keyboard_edit_list_user")
    button_1 = InlineKeyboardButton(text='Выдать', callback_data='get_key')
    button_2 = InlineKeyboardButton(text='Заменить', callback_data='change_key')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]],)
    return keyboard


def keyboard_select_category_keys() -> None:
    """
    КЛЮЧ - [Выдать] - Категории
    :return:
    """
    logging.info("keyboard_select_category_keys")
    button_1 = InlineKeyboardButton(text='Ключи Office', callback_data='getproduct_office')
    button_2 = InlineKeyboardButton(text='Ключи Office 365', callback_data='keyproduct_Office 365:0')
    button_3 = InlineKeyboardButton(text='Ключи Windows', callback_data='getproduct_windows')
    button_4 = InlineKeyboardButton(text='Ключи Project', callback_data='getproduct_project')
    button_5 = InlineKeyboardButton(text='Ключи Visio', callback_data='getproduct_visio')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_4], [button_5]],)
    return keyboard


def keyboards_list_product(list_product: list, category: str):
    logging.info("keyboards_list_product")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    print("category:", category)
    for i, product in enumerate(list_product):
        if category != 'windows' and category != 'office':
            callback = f'keyproduct_{category}:{i}'
        else:
            callback = f'typegive_{category}:{i}'
        print(callback)
        buttons.append(InlineKeyboardButton(
            text=product,
            callback_data=callback))
    button_back = InlineKeyboardButton(text='Назад',
                                       callback_data=f'pageback_category')
    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back)
    return kb_builder.as_markup()


def keyboards_list_type_office(category: str, product: int):
    logging.info("keyboards_list_type")
    button_1 = InlineKeyboardButton(text='Online', callback_data=f'keyproduct_{category}:{product}:onlineoffice')
    button_2 = InlineKeyboardButton(text='По телефону', callback_data=f'keyproduct_{category}:{product}:phoneoffice')
    button_3 = InlineKeyboardButton(text='Ключ с привязкой MS', callback_data=f'keyproduct_{category}:{product}:linkingMSoffice')
    button_back = InlineKeyboardButton(text='Назад', callback_data=f'pageback_productoffice')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_back]], )
    return keyboard


def keyboards_list_type_windows(category: str, product: int):
    logging.info("keyboards_list_type")
    button_1 = InlineKeyboardButton(text='Online', callback_data=f'keyproduct_{category}:{product}:onlinewindows')
    button_2 = InlineKeyboardButton(text='По телефону', callback_data=f'keyproduct_{category}:{product}:phonewindows')
    button_3 = InlineKeyboardButton(text='С привязкой', callback_data=f'keyproduct_{category}:{product}:linkingwindows')
    button_back = InlineKeyboardButton(text='Назад', callback_data=f'pageback_productwindows')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_back]], )
    return keyboard


def keyboards_cancel_key(category: str, product: int):
    logging.info("keyboards_list_type")
    button_1 = InlineKeyboardButton(text='Отмена', callback_data=f'cansel_get_key')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]], )
    return keyboard