from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters import or_f
import logging
from filter.admin_filter import chek_admin, chek_admin_1
from services.googlesheets import dict_category, get_list_product, get_key_product, get_key_product_office365
from config_data.config import Config, load_config

router = Router()
config: Config = load_config()


# ОСТАТОК
@router.message(F.text == 'Остаток', or_f(lambda message: chek_admin(message.chat.id),
                lambda message: chek_admin_1(message.chat.id)))
async def process_get_rest(message: Message) -> None:
    logging.info(f'process_get_rest: {message.chat.id}')
    dict_rest = {}

    for i, category in enumerate(dict_category):
        count_key = 0

        if category == 'Office 365':
            list_key = get_key_product_office365(category=category)
            for key in list_key:
                for k in key:
                    if k == '✅':
                        count_key += 1
            dict_rest['Office 365'] = count_key
            continue
        list_product = get_list_product(category)
        # print(list_product)
        for j, product in enumerate(list_product):
            # print(product)
            list_key = get_key_product(category=category, product=j)
            count_key = 0
            dict_rest[product] = {}
            if 'Office' in product:
                for key in list_key:
                    for k in key:
                        if k == '✅':
                            count_key += 1

                    if 'По телефону:' in key:
                        dict_rest[product]['Online'] = count_key
                        count_key = 0
                dict_rest[product]['По телефону'] = count_key
            elif 'Project' in product or 'Visio' in product:
                for key in list_key:
                    for k in key:
                        if k == '✅':
                            count_key += 1
                dict_rest[product]['Online'] = count_key
            else:
                for key in list_key:
                    for k in key:
                        if k == '✅':
                            count_key += 1
                    if 'С привязкой:' in key:
                        dict_rest[product]['Online'] = count_key
                        count_key = 0
                    if 'По телефону:' in key:
                        dict_rest[product]['С привязкой'] = count_key
                        count_key = 0
                dict_rest[product]['По телефону'] = count_key
            # print(dict_rest[product])
    text = ''
    for category in dict_rest:
        # print(category, dict_rest[category])
        if category == 'Office 365':
            text += f'<b>{category}:</b> {dict_rest[category]}\n' \
                    f'------------\n'
            continue
        if category == 'Office 2013 Professional Plus - Online:' or\
                category == 'Windows 7 Pro Retail - Ключ на 1 ПК (По телефону)' or\
                category == 'Windows 10 Pro MacOS - Ключ на 1 ПК (По телефону)' or \
                category == 'Office 2013 Professional Plus - Online' or\
                category == 'Аккаунт с облаком (без гарантии)':
            continue
        else:
            text += f'<b>{category}:</b>\n'
        for product in dict_rest[category]:

            text += f'<i>{product}</i> - {dict_rest[category][product]}\n'

        text += f'------------\n'
    await message.answer(text=text,
                         parse_mode='html')


async def process_sheduler(bot: Bot) -> None:
    dict_rest = {}
    for i, category in enumerate(dict_category):
        count_key = 0
        if category == 'Office 365':
            list_key = get_key_product_office365(category=category)
            for key in list_key:
                for k in key:
                    if k == '✅':
                        count_key += 1
            dict_rest['Office 365'] = count_key
            continue
        list_product = get_list_product(category)

        for j, product in enumerate(list_product):
            list_key = get_key_product(category=category, product=j)
            count_key = 0
            dict_rest[product] = {}
            if 'Office' in product:
                for key in list_key:
                    for k in key:
                        if k == '✅':
                            count_key += 1

                    if 'По телефону:' in key:
                        dict_rest[product]['Online'] = count_key
                        count_key = 0
                dict_rest[product]['По телефону'] = count_key
            else:
                for key in list_key:
                    for k in key:
                        if k == '✅':
                            count_key += 1
                    if 'С привязкой:' in key:
                        dict_rest[product]['Online'] = count_key
                        count_key = 0
                    if 'По телефону:' in key:
                        dict_rest[product]['С привязкой'] = count_key
                        count_key = 0
                dict_rest[product]['По телефону'] = count_key
    text = ''
    for category in dict_rest:

        if category == 'Office 365':
            text += f'<b>{category}:</b> {dict_rest[category]}\n' \
                    f'------------\n'
            continue
        if category == 'Office 2013 Professional Plus - Online:' or\
                category == 'Windows 7 Pro Retail - Ключ на 1 ПК (По телефону)' or\
                category == 'Windows 10 Pro MacOS - Ключ на 1 ПК (По телефону)' or \
                category == 'Office 2013 Professional Plus - Online' or\
                category == 'Аккаунт с облаком (без гарантии)':
            continue
        else:
            text += f'<b>{category}:</b>\n'
        for product in dict_rest[category]:

            text += f'<i>{product}</i> - {dict_rest[category][product]}\n'
        text += f'------------\n'
    for admin in config.tg_bot.admin_ids.split(','):
        await bot.send_message(chat_id=int(admin),
                               text=text,
                               parse_mode='html')
