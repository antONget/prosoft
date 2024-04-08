from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboard_select_category_set_keys() -> InlineKeyboardMarkup:
    """
    КЛЮЧ - [Выдать] - Категории
    :return:
    """
    logging.info("keyboard_select_category_set_keys")
    button_1 = InlineKeyboardButton(text='Ключи Office', callback_data='setproduct_office')
    button_2 = InlineKeyboardButton(text='Ключи Office 365', callback_data='setkeyproduct_Office 365:0')
    button_3 = InlineKeyboardButton(text='Ключи Windows', callback_data='setproduct_windows')
    button_4 = InlineKeyboardButton(text='Ключи Project', callback_data='setproduct_project')
    button_5 = InlineKeyboardButton(text='Ключи Visio', callback_data='setproduct_visio')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_4], [button_5]],)
    return keyboard


def keyboards_list_product_set_keys(list_product: list, category: str):
    logging.info("keyboards_list_product_set_keys")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    print("category:", category)
    for i, product in enumerate(list_product):
        if category != 'windows' and category != 'office':
            callback = f'setkeyproduct_{category}:{i}'
        else:
            callback = f'settypegive_{category}:{i}'
        print(callback)
        buttons.append(InlineKeyboardButton(
            text=product,
            callback_data=callback))
    button_back = InlineKeyboardButton(text='Назад',
                                       callback_data=f'setpageback_category')
    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back)
    return kb_builder.as_markup()


def keyboards_add_more_keys() -> InlineKeyboardMarkup:
    logging.info("keyboards_list_type_office_set_keys")
    button_1 = InlineKeyboardButton(text='Добавить ещё?', callback_data=f'add_more_keys')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]], )
    return keyboard


def keyboards_list_type_office_set_keys(category: str, product: int):
    logging.info("keyboards_list_type_office_set_keys")
    button_1 = InlineKeyboardButton(text='Online', callback_data=f'setkeyproduct_{category}:{product}:onlineoffice')
    button_2 = InlineKeyboardButton(text='По телефону', callback_data=f'setkeyproduct_{category}:{product}:phoneoffice')
    button_3 = InlineKeyboardButton(text='Ключ с привязкой MS', callback_data=f'setkeyproduct_{category}:{product}:linkingMSoffice')
    button_back = InlineKeyboardButton(text='Назад', callback_data=f'setpageback_productoffice')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_back]], )
    return keyboard


def keyboards_list_type_windows_set_keys(category: str, product: int):
    logging.info("keyboards_list_type_windows_set_keys")
    button_1 = InlineKeyboardButton(text='Online', callback_data=f'setkeyproduct_{category}:{product}:onlinewindows')
    button_2 = InlineKeyboardButton(text='По телефону', callback_data=f'setkeyproduct_{category}:{product}:phonewindows')
    button_3 = InlineKeyboardButton(text='С привязкой', callback_data=f'setkeyproduct_{category}:{product}:linkingwindows')
    button_back = InlineKeyboardButton(text='Назад', callback_data=f'setpageback_productwindows')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_back]], )
    return keyboard
