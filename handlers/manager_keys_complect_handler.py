from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.keyboard_key_complect import keyboard_select_category_keys, keyboards_list_product, \
    keyboards_list_type_office, keyboards_list_type_windows, keyboards_sale_complete
from services.googlesheets import get_list_product, get_key_product, get_cost_product, get_key_product_office365, \
    update_row_key_product, append_order, update_row_key_product_cancel
from module.data_base import get_list_users
from config_data.config import Config, load_config

import logging
import requests
from datetime import datetime, timedelta
from datetime import date
from secrets import token_urlsafe

router = Router()
user_dict = {}
config: Config = load_config()


def get_telegram_user(user_id, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    return response.json()


# <editor-fold desc = "СЕКЦИЯ (main keyboard -> [Ключ] -> [Комплект] - get_complete)">
# КЛЮЧ - [Комплект] - категории продуктов
@router.callback_query(F.data == 'get_complete')
async def process_select_category(callback: CallbackQuery) -> None:
    logging.info(f'process_select_category: {callback.message.chat.id}')
    try:
        await callback.message.edit_text(text='Выберите категорию продукта для получения ключа',
                                         reply_markup=keyboard_select_category_keys())
    except:
        await callback.message.edit_text(text='Выберитe категoрию продукта для получения ключа',
                                         reply_markup=keyboard_select_category_keys())


# КЛЮЧ - [Комплект] - категории - продукты
@router.callback_query(F.data.startswith('completegetproduct'))
async def process_select_product(callback: CallbackQuery) -> None:
    logging.info(f'process_select_product:{callback.data.split("_")[1]} {callback.message.chat.id} ')
    list_product = get_list_product(callback.data.split('_')[1])
    # print(list_product)
    if callback.data.split('_')[1] == 'windows':
        list_product = list_product[:2]
    if callback.data.split('_')[1] == 'office':
        list_product = list_product[:3]
    try:
        await callback.message.answer(text='Выберите продукт для получения ключа.',
                                      reply_markup=keyboards_list_product(list_product=list_product,
                                                                          category=callback.data.split('_')[1]))
    except:
        await callback.message.answer(text='Выберите прoдукт для пoлучения ключа',
                                      reply_markup=keyboards_list_product(list_product=list_product,
                                                                          category=callback.data.split('_')[1]))


# КЛЮЧ - [Комплект] - категории - продукт - способ выдачи (для office и windows)
@router.callback_query(F.data.startswith('completetypegive_'))
async def process_select_typegive(callback: CallbackQuery) -> None:
    logging.info(f'process_select_keyproduct: {callback.message.chat.id}')
    # product_{category}:{id_product}
    category = callback.data.split('_')[1].split(':')[0]
    id_product_in_category = int(callback.data.split('_')[1].split(':')[1])
    if category == 'office':
        await callback.message.answer(text=f'Выберите способ выдачи ключа:',
                                      reply_markup=keyboards_list_type_office(category=category,
                                                                              product=id_product_in_category))
    elif category == 'windows':
        await callback.message.answer(text=f'Выберите способ выдачи ключа:',
                                      reply_markup=keyboards_list_type_windows(category=category,
                                                                               product=id_product_in_category))


# КЛЮЧ - [Комплект] - категории - продукт - key
@router.callback_query(F.data.startswith('completekeyproduct_'))
async def process_select_keyproduct(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_select_keyproduct: {callback.message.chat.id}')
    # product_{category}:{id_product}
    category = callback.data.split('_')[1].split(':')[0]
    id_product_in_category = int(callback.data.split('_')[1].split(':')[1])
    if category == 'office':
        await process_select_key_office(callback=callback, category=category,
                                        id_product_in_category=id_product_in_category, state=state, bot=bot)
    elif category == 'windows':
        await process_select_key_windows(callback=callback, category=category,
                                         id_product_in_category=id_product_in_category, state=state, bot=bot)
    elif category == 'visio' or category == 'project':
        await process_select_key_visio_and_project(callback=callback, category=category,
                                                   id_product_in_category=id_product_in_category, state=state, bot=bot)
    else:
        await process_select_key_office365(callback=callback, category=category, state=state, bot=bot)


async def process_select_key_office(callback: CallbackQuery, category: str, id_product_in_category: int,
                                    state: FSMContext, bot: Bot):
    logging.info(f'process_select_key_office: {callback.message.chat.id}')
    list_key_product = get_key_product(category=category, product=id_product_in_category)

    list_key_online = []
    list_key_phone = []
    list_key_linkingMS = []
    dict_key_office = {
        "list_key_online": list_key_online,
        "list_key_phone": list_key_phone,
        "list_key_linkingMS": list_key_linkingMS
    }
    key = "list_key_online"
    for i, item in enumerate(list_key_product[1:]):
        if item[0] == 'По телефону:':
            key = "list_key_phone"
        if item[0] == 'С привязкой:':
            key = "list_key_linkingMS"

        dict_key_office[key].append(item)
    # print(dict_key_office)

    type_give = callback.data.split('_')[1].split(':')[2]
    # print(type_give)
    if type_give == 'onlineoffice':
        # print(dict_key_office["list_key_online"])

        count_pos = 0
        for key in dict_key_office["list_key_online"]:
            for pos in key:
                if pos == '✅':
                    count_pos += 1
        # print(f'Осталась ключей {count_pos}')
        await state.update_data(count_pos=count_pos)

        for key in dict_key_office["list_key_online"]:
            if '✅' in key and key[1] != '':
                # print(key[1])
                cost = get_cost_product(product=key[0], typelink=type_give)
                await get_key_product_finish(callback=callback, category=category, product=key[0],
                                             key_product=key[1], id_row_key=key[-1],
                                             id_product_in_category=id_product_in_category, cost=cost,
                                             type_give='online', bot=bot, state=state)
                break
        else:
            await callback.message.answer(text='Ключи по запрошенному продукту в таблице отсутствуют')

    elif type_give == 'phoneoffice':
        for key in dict_key_office["list_key_phone"]:
            if '✅' in key and key[1] != '':
                cost = get_cost_product(product=key[0], typelink=type_give)
                await get_key_product_finish(callback=callback, category=category, product=key[0],
                                             key_product=key[1], id_row_key=key[-1],
                                             id_product_in_category=id_product_in_category, cost=cost,
                                             type_give='phone', state=state, bot=bot)
                break
        else:
            await callback.message.answer(text='Ключи по запрошенному продукту в таблице отсутствуют')
    elif type_give == 'linkingMSoffice':
        # print(dict_key_office["list_key_linkingMS"])
        for key in dict_key_office["list_key_linkingMS"]:
            if '✅' in key and key[1] != '':
                # print(key[1])
                cost = get_cost_product(product=key[0], typelink=type_give)
                await get_key_product_finish(callback=callback, category=category, product=key[0],
                                             key_product=key[1], id_row_key=key[-1],
                                             id_product_in_category=id_product_in_category, cost=cost,
                                             type_give='linking', state=state, bot=bot)
                break
            else:
                await callback.message.answer(text='Обратитесь к руководителю для получения ключа')


async def process_select_key_windows(callback: CallbackQuery, category: str, id_product_in_category: int,
                                     state: FSMContext, bot: Bot):
    logging.info(f'process_select_key_windows: {callback.message.chat.id}')
    list_key_product = get_key_product(category=category, product=id_product_in_category)

    list_key_online = []
    list_key_phone = []
    list_key_linking = []
    dict_key_windows = {
        "list_key_online": list_key_online,
        "list_key_phone": list_key_phone,
        "list_key_linking": list_key_linking
    }
    key = "list_key_online"
    for i, item in enumerate(list_key_product[1:]):
        if item[0] == 'По телефону:':
            key = "list_key_phone"
        if item[0] == 'С привязкой:':
            key = "list_key_linking"

        dict_key_windows[key].append(item)
    # print(dict_key_office)

    type_give = callback.data.split('_')[1].split(':')[2]
    # print(type_give)
    if type_give == 'onlinewindows':
        # print(dict_key_windows["list_key_online"])

        count_pos = 0
        for key in dict_key_windows["list_key_online"]:
            for pos in key:
                if pos == '✅' and key[1] != '':
                    count_pos += 1
        # print(f'Осталась ключей {count_pos}')
        await state.update_data(count_pos=count_pos)

        for key in dict_key_windows["list_key_online"]:
            if '✅' in key and key[1] != '':
                # print(key[1])
                cost = get_cost_product(product=key[0], typelink=type_give)
                await get_key_product_finish(callback=callback, category=category, product=key[0],
                                             key_product=key[1], id_row_key=key[-1],
                                             id_product_in_category=id_product_in_category, cost=cost,
                                             type_give='online', bot=bot, state=state)
                break
        else:
            await callback.message.answer(text='Ключи по запрошенному продукту в таблице отсутствуют')

    elif type_give == 'phonewindows':
        # print(dict_key_windows["list_key_phone"])
        for key in dict_key_windows["list_key_phone"]:
            if '✅' in key and key[1] != '':
                # print(key[1])
                cost = get_cost_product(product=key[0], typelink=type_give)
                await get_key_product_finish(callback=callback, category=category, product=key[0],
                                             key_product=key[1], id_row_key=key[-1],
                                             id_product_in_category=id_product_in_category, cost=cost,
                                             type_give='phone', state=state, bot=bot)
                break
        else:
            await callback.message.answer(text='Ключи по запрошенному продукту в таблице отсутствуют')
    elif type_give == 'linkingwindows':

        count_pos = 0
        for key in dict_key_windows["list_key_linking"]:
            for pos in key:
                if pos == '✅' and key[1] != '':
                    count_pos += 1
        await state.update_data(count_pos=count_pos)

        for key in dict_key_windows["list_key_linking"]:
            if '✅' in key and key[1] != '':
                # print(key[1])
                cost = get_cost_product(product=key[0], typelink=type_give)
                await get_key_product_finish(callback=callback, category=category, product=key[0],
                                             key_product=key[1], id_row_key=key[-1],
                                             id_product_in_category=id_product_in_category, cost=cost,
                                             type_give='linking', state=state, bot=bot)
                break
        else:
            await callback.message.answer(text='Ключи по запрошенному продукту в таблице отсутствуют')


async def process_select_key_office365(callback: CallbackQuery, category: str, state: FSMContext, bot: Bot):
    logging.info(f'process_select_key_office365: {callback.message.chat.id}')
    list_key_product = get_key_product_office365(category=category)
    # print(list_key_product)
    count_pos = 0
    for key in list_key_product:
        for pos in key:
            if pos == '✅' and key[0] != '':
                count_pos += 1
    logging.info(f'Осталось ключей Office 365: {count_pos}')
    await state.update_data(count_pos=count_pos)
    for key in list_key_product:
        if '✅' in key and key[0] != '':
            # print(key[0])
            cost = get_cost_product(product='Office 365', typelink='None')
            await get_key_product_finish(callback=callback, category=category, product=category, key_product=key[0],
                                         id_row_key=key[-1], cost=cost, type_give='online', state=state, bot=bot)
            break
    else:
        await callback.message.answer(text='Ключи по запрошенному продукту в таблице отсутствуют')


async def process_select_key_visio_and_project(callback: CallbackQuery, category: str, id_product_in_category: int,
                                               state: FSMContext, bot: Bot):
    logging.info(f'process_select_key_visio_and_project: {callback.message.chat.id}')
    # получаем список ключей в таблице во вкладке категории и в столбце продукта
    list_key_product = get_key_product(category=category, product=id_product_in_category)[1:]
    # print(list_key_product)
    for key in list_key_product:
        if '✅' in key and key[1] != '':
            # print(key[1])
            cost = get_cost_product(product=key[0], typelink='online')
            await get_key_product_finish(callback=callback, category=category, product=key[0],
                                         key_product=key[1], id_row_key=key[-1],
                                         id_product_in_category=id_product_in_category, cost=cost, type_give='online',
                                         state=state, bot=bot)
            break
    else:
        await callback.message.answer(text='Ключи по запрошенному продукту в таблице отсутствуют')


async def get_key_product_finish(callback: CallbackQuery, category: str, product: str, key_product: str,
                                 id_row_key: int, cost: list, type_give: str, state: FSMContext, bot: Bot,
                                 id_product_in_category: int = -1) -> None:
    logging.info(f'get_key_product_finish: {callback.message.chat.id}')
    product_list = product.split()
    product = ' '.join(product_list)
    cost = '/'.join([cost[1], cost[0], cost[2], cost[3]])
    user_dict[callback.message.chat.id] = await state.update_data()
    if 'complect_key' in user_dict[callback.message.chat.id].keys():
        complect_key = user_dict[callback.message.chat.id]['complect_key']
        complect_key.append([product, key_product, cost])
    else:
        await state.update_data(complect_key=[[product, key_product, cost]])
    update_row_key_product(category=category, id_product_in_category=id_product_in_category, id_key=id_row_key)
    await callback.message.answer(text=f'Ключ для продукта {product} добавлен в комплект')
    await process_select_category(callback)

    if (category in ['office', 'windows'] and type_give == 'online') or\
            (category == 'windows' and type_give == 'linking') or (category == 'Office 365'):
        user_dict[callback.message.chat.id] = await state.get_data()
        count_pos = user_dict[callback.message.chat.id]['count_pos']
        await state.update_data(count_pos=count_pos - 1)
        print(count_pos)
        if count_pos == 3:
            list_user = get_list_users()
            for user in list_user:
                # print(user)
                result = get_telegram_user(user_id=user[0], bot_token=config.tg_bot.token)
                if 'result' in result:
                    if category == 'Office 365':
                        await bot.send_message(chat_id=int(user[0]),
                                               text=f'⚠️ Необходимо пополнить остаток {product}')
                    else:
                        await bot.send_message(chat_id=int(user[0]),
                                               text=f'⚠️ Необходимо пополнить остаток {product} {type_give} активация')


@router.callback_query(F.data.startswith('completepageback_'))
async def process_select_back(callback: CallbackQuery) -> None:
    logging.info(f'process_select_back: {callback.message.chat.id}')
    back = callback.data.split('_')[1]
    if back == 'category':
        await process_select_category(callback)
    elif back == 'productoffice':
        logging.info(f'process_select_productoffice: {callback.message.chat.id}')
        list_product = get_list_product('office')
        await callback.message.edit_text(text='Выберите продукт для получения ключа',
                                         reply_markup=keyboards_list_product(list_product=list_product,
                                                                             category='office'))
    elif back == 'productwindows':
        logging.info(f'process_select_productwindows: {callback.message.chat.id}')
        list_product = get_list_product('windows')
        await callback.message.edit_text(text='Выберите продукт для получения ключа',
                                         reply_markup=keyboards_list_product(list_product=list_product,
                                                                             category='windows'))


@router.callback_query(F.data.startswith('completegivekey'))
async def process_select_sale_complete(callback: CallbackQuery) -> None:
    logging.info(f'process_select_sale_complete: {callback.message.chat.id} ')
    await callback.message.answer(text='Выберите скидку для комплекта ключей',
                                  reply_markup=keyboards_sale_complete())


@router.callback_query(F.data.startswith('completesale_'))
async def process_select_product(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_select_product: {callback.message.chat.id} ')
    user_dict[callback.message.chat.id] = await state.update_data()
    print(user_dict[callback.message.chat.id]['complect_key'])
    comlect = user_dict[callback.message.chat.id]['complect_key']
    current_date = datetime.now()
    current_date_string = current_date.strftime('%m/%d/%y %H:%M:%S')
    token_order = str(token_urlsafe(8))
    text = ''
    key_list = []
    price = 0
    cost_price = 0
    marginality = 0
    net_profit = 0
    sale = 1
    if callback.data.split('_')[1] == '15':
        await callback.message.answer(text='Применена скидка в 15% к заказу')
        sale = 0.85
    for key in comlect:
        text += key[0] + ': ' + key[1] + '\n'
        key_list.append(key[1])
        # цена продажи ключа без скидки
        price_ = float(key[2].split('/')[0].split('.')[0])
        # цена продажи ключа со скидкой
        price += (price_ * sale)
        # себестоимость ключа
        cost_price += float(key[2].split('/')[1].split('.')[0])
        # маржинальность
        # marginality += (int(key[2].split('/')[1].split('.')[0]) / (price_ * sale))
        # чистая прибыль
        net_profit += (price_ * sale - float(key[2].split('/')[1].split('.')[0]))
    if callback.data.split('_')[1] != 'cancel':
        marg = round(net_profit / price * 100, 2)
        cost = f'{price} ₽/{cost_price} ₽/{marg}/{net_profit} ₽'
        await callback.message.answer(text=f'Вы запрашивали комплект ключей:\n'
                                           f'<code>Номер заказа: {token_order}\n'
                                           f'{text}</code>', parse_mode='html')
        key_product = '$'.join(key_list)
        if callback.message.chat.id != 6392664243:
            append_order(id_order=token_order, date=current_date_string.split()[0], time=current_date_string.split()[1],
                         username=callback.from_user.username, key=key_product, cost=cost, category='Complect',
                         product='Complect',
                         type_give='complete', id_product='0')
        user_dict[callback.message.chat.id]['complect_key'] = []
    else:
        for key_item in comlect:
            if key_item[0] == 'Office 365':
                update_row_key_product_cancel(category='Office 365', key=key_item[1])
            else:
                category = key_item[0].split()[0].lower()
                update_row_key_product_cancel(category=category, key=key_item[1])
        await callback.message.answer(text=f'Запрашиваемый комплект ключей:\n'
                                           f'<code>Номер заказа: {token_order}\n'
                                           f'{text}</code>\nОтменен', parse_mode='html')
# @router.callback_query(F.data.startswith('completecancel_get_key'))
# async def process_cancel_get_key(callback: CallbackQuery) -> None:
#     logging.info(f'process_cancel_get_key: {callback.message.chat.id}')
#     id_order = callback.data.split('#')[1]
#     info_order = get_info_order(id_order)
#     list_key = info_order[4].split(',')
#     # print(list_key)
#     for key in list_key:
#         update_row_key_product_cancel(category=info_order[6], key=key)
#     delete_row_order(id_order=id_order)
#     await callback.message.edit_text(text='Активация ключа в таблице восстановлена')


# @router.callback_query(F.data.startswith('completeappend_get_key'))
# async def process_append_get_key(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
#     logging.info(f'process_cancel_get_key: {callback.message.chat.id}')
#     id_order = callback.data.split('#')[1]
#     info_order = get_info_order(id_order)
#     if info_order:
#         # print(info_order)
#         new_key = ''
#
#         if info_order[6] == 'Office 365':
#             list_key = get_key_product_office365(info_order[6])
#             for key in list_key:
#                 # print(key)
#                 if key[1] == '✅':
#                     new_key = key[0]
#                     update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
#                                            id_key=key[-1])
#                     count_pos = user_dict[callback.message.chat.id]['count_pos']
#                     await state.update_data(count_pos=count_pos - 1)
#                     break
#         elif info_order[6] == 'office' or info_order[6] == 'windows':
#             list_key = get_key_product(category=info_order[6], product=int(info_order[9]))
#             type_give = info_order[8]
#             list_key_online = []
#             list_key_phone = []
#             list_key_linking = []
#             dict_key_office = {
#                 "list_key_online": list_key_online,
#                 "list_key_phone": list_key_phone,
#                 "list_key_linking": list_key_linking
#             }
#             key = "list_key_online"
#             for i, item in enumerate(list_key[1:]):
#                 if item[0] == 'По телефону:':
#                     key = "list_key_phone"
#                 if item[0] == 'С привязкой:':
#                     key = "list_key_linking"
#
#                 dict_key_office[key].append(item)
#
#             if type_give == 'online':
#                 for key in dict_key_office["list_key_online"]:
#                     if '✅' in key and key[1] != '':
#                         new_key = key[1]
#                         update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
#                                                id_key=key[-1])
#                         count_pos = user_dict[callback.message.chat.id]['count_pos']
#                         await state.update_data(count_pos=count_pos - 1)
#                         break
#
#             if type_give == 'phone':
#                 # print(dict_key_office["list_key_online"])
#                 for key in dict_key_office["list_key_phone"]:
#                     if '✅' in key and key[1] != '':
#                         new_key = key[1]
#                         update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
#                                                id_key=key[-1])
#
#                         break
#             if type_give == 'linking':
#                 # print(dict_key_office["list_key_online"])
#                 for key in dict_key_office["list_key_linking"]:
#                     if '✅' in key and key[1] != '':
#                         new_key = key[1]
#                         update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
#                                                id_key=key[-1])
#                         count_pos = user_dict[callback.message.chat.id]['count_pos']
#                         await state.update_data(count_pos=count_pos - 1)
#                         break
#
#         elif info_order[6] == 'visio' or info_order[6] == 'project':
#             list_key = get_key_product(category=info_order[6], product=int(info_order[9]))
#             for key in list_key:
#                 if '✅' in key and key[1] != '':
#                     new_key = key[1]
#                     update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
#                                            id_key=key[-1])
#                     break
#         text_old = callback.message.text
#         text_old_list = text_old.split('\n')
#         text_old_list = [i for i in text_old_list if i]
#         len_key = len(text_old_list)
#         if len_key == 5:
#             text_old_list[2] = f'1№ {text_old_list[2]}'
#         text_old_list.insert(-2, f'{len_key-3}№ {new_key}')
#         text_old_list.insert(1, '<code>')
#         text_old_list.insert(-1, '</code>')
#         text_new = '\n'.join(text_old_list)
#
#         await callback.message.edit_text(text=f'{text_new}',
#                                          reply_markup=keyboards_cancel_append_key(id_order=info_order[0]),
#                                          parse_mode='html')
#         category = info_order[6]
#         product = info_order[7]
#         type_give = info_order[8]
#         if (category in ['office', 'windows'] and type_give == 'online') or \
#                 (category == 'windows' and type_give == 'linking') or (category == 'Office 365'):
#             user_dict[callback.message.chat.id] = await state.get_data()
#             count_pos = user_dict[callback.message.chat.id]['count_pos']
#             print(count_pos)
#             if count_pos == 3:
#                 list_user = get_list_users()
#                 for user in list_user:
#                     # print(user)
#                     result = get_telegram_user(user_id=user[0], bot_token=config.tg_bot.token)
#                     if 'result' in result:
#                         if category == 'Office 365':
#                             await bot.send_message(chat_id=int(user[0]),
#                                                    text=f'⚠️ Необходимо пополнить остаток {product}')
#                         else:
#                             await bot.send_message(chat_id=int(user[0]),
#                                                    text=f'⚠️ Необходимо пополнить остаток {product} {type_give} активация')
#
#         list_get_key = [info_order[4]]
#         list_get_key.append(new_key)
#         # print(list_get_key)
#         update_row_order_listkey(id_order=id_order, listkey=','.join(list_get_key))
#
#         if new_key == '':
#             await callback.message.answer(text="Ключи выбранного продукта закончились")
# </editor-fold>