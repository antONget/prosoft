from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter
import logging
from secrets import token_urlsafe
import asyncio
from module.data_base import add_token, get_list_users, get_user, delete_user
from datetime import datetime

from keyboards.keyboards_keys import keyboard_select_type_keys, keyboard_select_category_keys, keyboards_list_product, \
    keyboards_list_type_windows, keyboards_list_type_office, keyboards_cancel_append_key
from keyboards.keyboard_key_hand import keyboard_select_category_handkeys, keyboard_select_office_handkeys, \
    keyboard_select_windows_handkeys, keyboard_select_server_handkeys, keyboard_select_visio_handkeys, \
    keyboard_select_project_handkeys
from filter.user_filter import check_user
from services.googlesheets import get_list_product, get_key_product, get_key_product_office365, append_order,\
    update_row_key_product, get_cost_product, get_info_order, update_row_key_product_new_key, \
    update_row_key_product_cancel, delete_row_order, update_row_order_listkey, get_values_hand_product


router = Router()
user_dict = {}
class Keys(StatesGroup):
    get_id_order = State()
    get_key_hand = State()


# КЛЮЧ
@router.message(F.text == 'Получить ключ', lambda message: check_user(message.chat.id))
async def process_get_keys(message: Message) -> None:
    logging.info(f'process_get_keys: {message.chat.id}')
    """
    Функция позволяет получить новый ключ или заменить ранее выданный
    :param message:
    :return:
    """
    await message.answer(text="Что требуется сделать с ключем?",
                         reply_markup=keyboard_select_type_keys())


# КЛЮЧ - [Заменить]
@router.callback_query(F.data == 'change_key', lambda callback: check_user(callback.message.chat.id))
async def process_change_keys(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_get_keys: {callback.message.chat.id}')
    await callback.message.answer(text='Пришлите номер заказа для которого нужно заменить ключ')
    await state.set_state(Keys.get_id_order)


# КЛЮЧ - [Заменить] - номер заказа
@router.message(F.text, lambda message: check_user(message.chat.id), StateFilter(Keys.get_id_order))
async def process_get_id_order(message: Message, state: FSMContext) -> None:
    logging.info(f'process_get_id_order: {message.chat.id}')
    info_order = get_info_order(message.text)
    if info_order:
        print(info_order)
        await message.answer(text=f'№ заказa: {info_order[0]}\n'
                                  f'дата: {info_order[1]}-{info_order[2]}\n'
                                  f'Менеджер: {info_order[3]}\n'
                                  f'Ключ: <code>{info_order[4]}</code>\n'
                                  f'Стоимость: {info_order[5]}\n'
                                  f'Категория {info_order[6]} - продукт {info_order[7]}',
                             parse_mode='html')
        new_key = ''
        if info_order[6] == 'Office 365':
            list_key = get_key_product_office365(info_order[6])
            for key in list_key:
                print(key)
                if key[1] == '✅':
                    new_key = key[0]
                    update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
                                           id_key=key[-1])
                    break
        elif info_order[6] == 'office' or info_order[6] == 'windows':
            list_key = get_key_product(category=info_order[6], product=int(info_order[9]))
            type_give = info_order[8]
            list_key_online = []
            list_key_phone = []
            list_key_linking = []
            dict_key_office = {
                "list_key_online": list_key_online,
                "list_key_phone": list_key_phone,
                "list_key_linking": list_key_linking
            }
            key = "list_key_online"
            for i, item in enumerate(list_key[1:]):
                if item[0] == 'По телефону:':
                    key = "list_key_phone"
                if item[0] == 'С привязкой:':
                    key = "list_key_linking"

                dict_key_office[key].append(item)

            if type_give == 'online':
                # print(dict_key_office["list_key_phone"])
                for key in dict_key_office["list_key_online"]:
                    if '✅' in key and key[1] != '':
                        new_key = key[1]
                        update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
                                               id_key=key[-1])
                        break
            if type_give == 'phone':
                # print(dict_key_office["list_key_online"])
                for key in dict_key_office["list_key_phone"]:
                    if '✅' in key and key[1] != '':
                        new_key = key[1]
                        update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
                                               id_key=key[-1])
                        break
            if type_give == 'linking':
                # print(dict_key_office["list_key_online"])
                for key in dict_key_office["list_key_linking"]:
                    if '✅' in key and key[1] != '':
                        new_key = key[1]
                        update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
                                               id_key=key[-1])
                        break

        elif info_order[6] == 'visio' or info_order[6] == 'project':
            list_key = get_key_product(category=info_order[6], product=int(info_order[9]))
            for key in list_key:
                if '✅' in key and key[1] != '':
                    new_key = key[1]
                    update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
                                           id_key=key[-1])
                    break

        await message.answer(text=f'Новый ключ: <code>{new_key}</code>', parse_mode='html')
        update_row_key_product_new_key(new_key=new_key, id_order=message.text)
        # if info_order[6] == 'Office 365':
        #     list_key_product = get_key_product_office365(category=info_order[6])
        # else:
        #     list_key_product = get_key_product(category=info_order[6], product=int(info_order[9]))
        # print(list_key_product)
        # for key in list_key_product:
        #     if '✅' in key and key[1] != '':
        #         print(key[1])
        #         update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]), id_key=key[-1])
        #         break
        await state.set_state(default_state)
    else:
        await message.answer(text="Заказ не найден, повторите ввод")



# КЛЮЧ - [Выдать] - категории продуктов
@router.callback_query(F.data == 'get_key', lambda callback: check_user(callback.message.chat.id))
async def process_select_category(callback: CallbackQuery) -> None:
    logging.info(f'process_select_category: {callback.message.chat.id}')
    await callback.message.edit_text(text='Выберите категорию продукта для получения ключа',
                                     reply_markup=keyboard_select_category_keys())


# КЛЮЧ - [Выдать] - категории - продукты
@router.callback_query(F.data.startswith('getproduct'), lambda callback: check_user(callback.message.chat.id))
async def process_select_product(callback: CallbackQuery) -> None:
    logging.info(f'process_select_product: {callback.message.chat.id}')
    list_product = get_list_product(callback.data.split('_')[1])
    print(list_product)
    if callback.data.split('_')[1] == 'windows':
        list_product = list_product[:2]
    if callback.data.split('_')[1] == 'office':
        list_product = list_product[:3]
    await callback.message.edit_text(text='Выберите продукт для получения ключа',
                                     reply_markup=keyboards_list_product(list_product=list_product,
                                                                         category=callback.data.split('_')[1]))


# КЛЮЧ - [Выдать] - категории - продукт - способ выдачи (для office и windows)
@router.callback_query(F.data.startswith('typegive_'), lambda callback: check_user(callback.message.chat.id))
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


# КЛЮЧ - [Выдать] - категории - продукт - key
@router.callback_query(F.data.startswith('keyproduct_'), lambda callback: check_user(callback.message.chat.id))
async def process_select_keyproduct(callback: CallbackQuery) -> None:
    logging.info(f'process_select_keyproduct: {callback.message.chat.id}')
    # product_{category}:{id_product}
    category = callback.data.split('_')[1].split(':')[0]
    id_product_in_category = int(callback.data.split('_')[1].split(':')[1])
    if category == 'office':
        await process_select_key_office(callback=callback, category=category, id_product_in_category=id_product_in_category)
    elif category == 'windows':
        await process_select_key_windows(callback=callback, category=category, id_product_in_category=id_product_in_category)
    elif category == 'visio' or category == 'project':
        await process_select_key_visio_and_project(callback=callback, category=category, id_product_in_category=id_product_in_category)
    else:
        await process_select_key_office365(callback=callback, category=category)


async def process_select_key_office(callback: CallbackQuery, category: str, id_product_in_category: int):
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
        print(dict_key_office["list_key_online"])
        for key in dict_key_office["list_key_online"]:
            if '✅' in key and key[1] != '':
                print(key[1])
                cost = get_cost_product(product=key[0], typelink=type_give)
                await get_key_product_finish(callback=callback, category=category, product=key[0],
                                             key_product=key[1], id_row_key=key[-1],
                                             id_product_in_category=id_product_in_category, cost=cost,
                                             type_give='online')
                break
        else:
            await callback.message.answer(text='Ключи по запрошенному продукту в таблице отсутствуют')
    elif type_give == 'phoneoffice':
        print(dict_key_office["list_key_phone"])
        for key in dict_key_office["list_key_phone"]:
            if '✅' in key and key[1] != '':
                print(key[1])
                cost = get_cost_product(product=key[0], typelink=type_give)
                await get_key_product_finish(callback=callback, category=category, product=key[0],
                                             key_product=key[1], id_row_key=key[-1],
                                             id_product_in_category=id_product_in_category, cost=cost,
                                             type_give='phone')
                break
        else:
            await callback.message.answer(text='Ключи по запрошенному продукту в таблице отсутствуют')
    elif type_give == 'linkingMSoffice':
        print(dict_key_office["list_key_linkingMS"])
        for key in dict_key_office["list_key_linkingMS"]:
            if '✅' in key and key[1] != '':
                print(key[1])
                cost = get_cost_product(product=key[0], typelink=type_give)
                await get_key_product_finish(callback=callback, category=category, product=key[0],
                                             key_product=key[1], id_row_key=key[-1],
                                             id_product_in_category=id_product_in_category, cost=cost,
                                             type_give='linking')
                break
            else:
                await callback.message.answer(text='Обратитесь к руководителю для получения ключа')


async def process_select_key_windows(callback: CallbackQuery, category: str, id_product_in_category: int):
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
        print(dict_key_windows["list_key_online"])
        for key in dict_key_windows["list_key_online"]:
            if '✅' in key and key[1] != '':
                print(key[1])
                cost = get_cost_product(product=key[0], typelink=type_give)
                await get_key_product_finish(callback=callback, category=category, product=key[0],
                                             key_product=key[1], id_row_key=key[-1],
                                             id_product_in_category=id_product_in_category, cost=cost,
                                             type_give='online')
                break
        else:
            await callback.message.answer(text='Ключи по запрошенному продукту в таблице отсутствуют')
    elif type_give == 'phonewindows':
        print(dict_key_windows["list_key_phone"])
        for key in dict_key_windows["list_key_phone"]:
            if '✅' in key and key[1] != '':
                print(key[1])
                cost = get_cost_product(product=key[0], typelink=type_give)
                await get_key_product_finish(callback=callback, category=category, product=key[0],
                                             key_product=key[1], id_row_key=key[-1],
                                             id_product_in_category=id_product_in_category, cost=cost,
                                             type_give='phone')
                break
        else:
            await callback.message.answer(text='Ключи по запрошенному продукту в таблице отсутствуют')
    elif type_give == 'linkingwindows':
        print(dict_key_windows["list_key_linking"])
        for key in dict_key_windows["list_key_linking"]:
            if '✅' in key and key[1] != '':
                print(key[1])
                cost = get_cost_product(product=key[0], typelink=type_give)
                await get_key_product_finish(callback=callback, category=category, product=key[0],
                                             key_product=key[1], id_row_key=key[-1],
                                             id_product_in_category=id_product_in_category, cost=cost,
                                             type_give='linking')
                break
        else:
            await callback.message.answer(text='Ключи по запрошенному продукту в таблице отсутствуют')


async def process_select_key_office365(callback: CallbackQuery, category: str):
    logging.info(f'process_select_key_office365: {callback.message.chat.id}')
    list_key_product = get_key_product_office365(category=category)
    print(list_key_product)
    for key in list_key_product:
        if '✅' in key and key[0] != '':
            print(key[0])
            cost = get_cost_product(product='Office 365', typelink='None')
            await get_key_product_finish(callback=callback, category=category, product=category, key_product=key[0],
                                         id_row_key=key[-1], cost=cost, type_give='online')
            break
    else:
        await callback.message.answer(text='Ключи по запрошенному продукту в таблице отсутствуют')


async def process_select_key_visio_and_project(callback: CallbackQuery, category: str, id_product_in_category: int):
    logging.info(f'process_select_key_visio_and_project: {callback.message.chat.id}')
    # получаем список ключей в таблице во вкладке категории и в столбце продукта
    list_key_product = get_key_product(category=category, product=id_product_in_category)[1:]
    print(list_key_product)
    for key in list_key_product:
        if '✅' in key and key[1] != '':
            print(key[1])
            cost = get_cost_product(product=key[0], typelink='online')
            await get_key_product_finish(callback=callback, category=category, product=key[0],
                                         key_product=key[1], id_row_key=key[-1],
                                         id_product_in_category=id_product_in_category, cost=cost, type_give='online')
            break
    else:
        await callback.message.answer(text='Ключи по запрошенному продукту в таблице отсутствуют')


async def get_key_product_finish(callback: CallbackQuery, category: str, product: str, key_product: str,
                                 id_row_key: int, cost: str, type_give: str, id_product_in_category: int = -1) -> None:
    logging.info(f'get_key_product_finish: {callback.message.chat.id}')
    token_order = str(token_urlsafe(8))
    current_date = datetime.now()
    product_list = product.split()
    product = ' '.join(product_list)
    current_date_string = current_date.strftime('%m/%d/%y %H:%M:%S')
    append_order(id_order=token_order, date=current_date_string.split()[0], time=current_date_string.split()[1],
                 username=callback.from_user.username, key=key_product, cost=cost, category=category, product=product,
                 type_give=type_give, id_product=id_product_in_category)
    key_product_ = key_product
    if category == 'Office 365':
        key_product_ = key_product.split(':')[2]
    await callback.message.answer(text=f'Вы запрашивали:\n'
                                       f'<code>Ключ для {product}\n'
                                       f'{key_product}\n'
                                       f'Номер заказа: {token_order}</code>\n'
                                       f'отправьте его заказчику',
                                  reply_markup=keyboards_cancel_append_key(id_order=token_order),
                                  parse_mode='html')
    update_row_key_product(category=category, id_product_in_category=id_product_in_category, id_key=id_row_key)


@router.callback_query(F.data.startswith('pageback_'), lambda callback: check_user(callback.message.chat.id))
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


@router.callback_query(F.data.startswith('cancel_get_key'), lambda callback: check_user(callback.message.chat.id))
async def process_cancel_get_key(callback: CallbackQuery) -> None:
    logging.info(f'process_cancel_get_key: {callback.message.chat.id}')
    id_order = callback.data.split('#')[1]
    info_order = get_info_order(id_order)
    list_key = info_order[4].split(',')
    print(list_key)
    for key in list_key:
        update_row_key_product_cancel(category=info_order[6], key=key)
    delete_row_order(id_order=id_order)
    await callback.message.edit_text(text='Активация ключа в таблице восстановлена')


@router.callback_query(F.data.startswith('append_get_key'), lambda callback: check_user(callback.message.chat.id))
async def process_append_get_key(callback: CallbackQuery) -> None:
    logging.info(f'process_cancel_get_key: {callback.message.chat.id}')
    id_order = callback.data.split('#')[1]
    info_order = get_info_order(id_order)
    if info_order:
        print(info_order)
        new_key = ''
        if info_order[6] == 'Office 365':
            list_key = get_key_product_office365(info_order[6])
            for key in list_key:
                print(key)
                if key[1] == '✅':
                    new_key = key[0]
                    update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
                                           id_key=key[-1])
                    break
        elif info_order[6] == 'office' or info_order[6] == 'windows':
            list_key = get_key_product(category=info_order[6], product=int(info_order[9]))
            type_give = info_order[8]
            list_key_online = []
            list_key_phone = []
            list_key_linking = []
            dict_key_office = {
                "list_key_online": list_key_online,
                "list_key_phone": list_key_phone,
                "list_key_linking": list_key_linking
            }
            key = "list_key_online"
            for i, item in enumerate(list_key[1:]):
                if item[0] == 'По телефону:':
                    key = "list_key_phone"
                if item[0] == 'С привязкой:':
                    key = "list_key_linking"

                dict_key_office[key].append(item)

            if type_give == 'online':
                # print(dict_key_office["list_key_phone"])
                for key in dict_key_office["list_key_online"]:
                    if '✅' in key and key[1] != '':
                        new_key = key[1]
                        update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
                                               id_key=key[-1])
                        break
            if type_give == 'phone':
                # print(dict_key_office["list_key_online"])
                for key in dict_key_office["list_key_phone"]:
                    if '✅' in key and key[1] != '':
                        new_key = key[1]
                        update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
                                               id_key=key[-1])
                        break
            if type_give == 'linking':
                # print(dict_key_office["list_key_online"])
                for key in dict_key_office["list_key_linking"]:
                    if '✅' in key and key[1] != '':
                        new_key = key[1]
                        update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
                                               id_key=key[-1])
                        break

        elif info_order[6] == 'visio' or info_order[6] == 'project':
            list_key = get_key_product(category=info_order[6], product=int(info_order[9]))
            for key in list_key:
                if '✅' in key and key[1] != '':
                    new_key = key[1]
                    update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
                                           id_key=key[-1])
                    break
        text_old = callback.message.text
        text_old_list = text_old.split('\n')
        text_old_list = [i for i in text_old_list if i]
        text_old_list.insert(2, new_key)
        text_old_list.insert(1, '<code>')
        text_old_list.insert(-1, '</code>')
        text_new = '\n'.join(text_old_list)

        # f'Вы запрашивали:\n'
        # f'<code>Ключ для {product}\n'
        # f'{key_product}\n'
        # f'Номер заказа: {token_order}</code>\n'
        # f'отправьте его заказчику',
        print(text_new)
        key_product_ = new_key
        if info_order[6] == 'Office 365':
            key_product_ = new_key.split(':')[2]
        await callback.message.edit_text(text=f'{text_new}',
                                         reply_markup=keyboards_cancel_append_key(id_order=info_order[0]),
                                         parse_mode='html')
        list_get_key = [info_order[4]]
        list_get_key.append(new_key)
        print(list_get_key)
        update_row_order_listkey(id_order=id_order, listkey=','.join(list_get_key))


        if new_key == '':
            await callback.message.answer(text="Ключи выбранного продукта закончились")


# КЛЮЧ - [Ручной ввод] - Категория
@router.callback_query(F.data == 'hand_key', lambda callback: check_user(callback.message.chat.id))
async def process_hand_keys(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_hand_keys: {callback.message.chat.id}')
    await callback.message.answer(text='Выберите категорию для ручного ввода',
                                  reply_markup=keyboard_select_category_handkeys())


# КЛЮЧ - [Ручной ввод] - Категория - Продукт
@router.callback_query(F.data.startswith('handgetproduct_'), lambda callback: check_user(callback.message.chat.id))
async def process_hand_keys_product(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_hand_keys_product: {callback.message.chat.id}')
    category = callback.data.split('_')[1]
    keyboard = 0
    if category == 'office':
        keyboard = keyboard_select_office_handkeys()
    elif category == 'windows':
        keyboard = keyboard_select_windows_handkeys()
    elif category == 'server':
        keyboard = keyboard_select_server_handkeys()
    elif category == 'visio':
        keyboard = keyboard_select_visio_handkeys()
    elif category == 'project':
        keyboard = keyboard_select_project_handkeys()
    await state.update_data(category_hand=category)
    await callback.message.edit_text(text='Выберите продукт:',
                                     reply_markup=keyboard)


# КЛЮЧ - [Ручной ввод] - Категория - Продукт - Добавить ключ
@router.callback_query(F.data.startswith('handgetkey'), lambda callback: check_user(callback.message.chat.id))
async def process_hand_keys_product(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_hand_keys_product: {callback.message.chat.id}')
    # category = callback.data.split('#')[1]
    product = callback.data.split('#')[1]
    cost_hand = get_values_hand_product(product)
    await state.update_data(cost_hand=cost_hand)
    await state.update_data(product_hand=product)
    await callback.message.answer(text=f'Пришлите ключ для добавления')
    await state.set_state(Keys.get_key_hand)


@router.message(F.text, StateFilter(Keys.get_key_hand))
async def process_input_get_key_hand(message: Message, state: FSMContext):
    logging.info(f'process_input_get_key_hand: {message.chat.id}')
    user_dict[message.chat.id] = await state.get_data()
    token_order = str(token_urlsafe(8))
    current_date = datetime.now()
    current_date_string = current_date.strftime('%m/%d/%y %H:%M:%S')
    append_order(id_order=token_order,
                 date=current_date_string.split()[0],
                 time=current_date_string.split()[1],
                 username=message.from_user.username,
                 key=message.text,
                 cost=user_dict[message.chat.id]['cost_hand'],
                 category=user_dict[message.chat.id]['category_hand'],
                 product=user_dict[message.chat.id]['product_hand'],
                 type_give='hand',
                 id_product='-')
    await state.set_state(default_state)