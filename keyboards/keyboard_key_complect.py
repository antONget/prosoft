from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboard_select_category_keys() -> InlineKeyboardMarkup:
    """
    КЛЮЧ - [Выдать] - Категории
    :return:
    """
    logging.info("keyboard_select_category_keys")
    button_1 = InlineKeyboardButton(text='Ключи Office', callback_data='completegetproduct_office')
    button_2 = InlineKeyboardButton(text='Ключи Office 365', callback_data='completekeyproduct_Office 365:0')
    button_3 = InlineKeyboardButton(text='Ключи Windows', callback_data='completegetproduct_windows')
    button_4 = InlineKeyboardButton(text='Ключи Project', callback_data='completegetproduct_project')
    button_5 = InlineKeyboardButton(text='Ключи Visio', callback_data='completegetproduct_visio')
    button_6 = InlineKeyboardButton(text='Выдать комлект ключей', callback_data='completegivekey')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_4], [button_5],
                                                     [button_6]],)
    return keyboard


def keyboards_list_product(list_product: list, category: str):
    logging.info("keyboards_list_product")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    print("category:", category)
    for i, product in enumerate(list_product):
        if category != 'windows' and category != 'office':
            callback = f'completekeyproduct_{category}:{i}'
        else:
            callback = f'completetypegive_{category}:{i}'
        print(callback)
        buttons.append(InlineKeyboardButton(
            text=product,
            callback_data=callback))
    button_back = InlineKeyboardButton(text='Назад',
                                       callback_data=f'completepageback_category')
    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back)
    return kb_builder.as_markup()


def keyboards_list_type_office(category: str, product: int):
    logging.info("keyboards_list_type")
    button_1 = InlineKeyboardButton(text='Online', callback_data=f'completekeyproduct_{category}:{product}:onlineoffice')
    button_2 = InlineKeyboardButton(text='По телефону', callback_data=f'completekeyproduct_{category}:{product}:phoneoffice')
    button_3 = InlineKeyboardButton(text='Ключ с привязкой MS', callback_data=f'completekeyproduct_{category}:{product}:linkingMSoffice')
    button_back = InlineKeyboardButton(text='Назад', callback_data=f'completepageback_productoffice')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_back]], )
    return keyboard


def keyboards_list_type_windows(category: str, product: int):
    logging.info("keyboards_list_type")
    button_1 = InlineKeyboardButton(text='Online', callback_data=f'completekeyproduct_{category}:{product}:onlinewindows')
    button_2 = InlineKeyboardButton(text='По телефону', callback_data=f'completekeyproduct_{category}:{product}:phonewindows')
    button_3 = InlineKeyboardButton(text='С привязкой', callback_data=f'completekeyproduct_{category}:{product}:linkingwindows')
    button_back = InlineKeyboardButton(text='Назад', callback_data=f'completepageback_productwindows')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_back]], )
    return keyboard


def keyboards_cancel_append_key(id_order: str):
    logging.info("keyboards_cancel_append_key")
    button_1 = InlineKeyboardButton(text='Отмена', callback_data=f'completecancel_get_key#{id_order}')
    button_2 = InlineKeyboardButton(text='Выдать ещё один ключ', callback_data=f'completeappend_get_key#{id_order}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]], )
    return keyboard


def keyboards_cancel_get_key(id_order: str):
    logging.info("keyboards_cancel_get_key")
    button_1 = InlineKeyboardButton(text='Отменить выдачу ключа', callback_data=f'completecancel_get_key#{id_order}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]], )
    return keyboard


def keyboards_sale_complete():
    logging.info("keyboards_sale_complete")
    button_1 = InlineKeyboardButton(text='Выдать комплект со скидкой -15%', callback_data=f'completesale_15')
    button_2 = InlineKeyboardButton(text='Выдать комплект без скидки', callback_data=f'completesale_0')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]], )
    return keyboard
