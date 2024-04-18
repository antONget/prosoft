from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter

from keyboards.keyboards_keys import keyboard_select_action_keys_manager, keyboard_select_action_keys_admin, \
    keyboard_select_category_keys, keyboards_list_product, \
    keyboards_list_type_windows, keyboards_list_type_office, keyboards_cancel_append_key, keyboards_cancel_get_key
from keyboards.keyboard_key_hand import keyboard_select_category_handkeys, keyboard_select_office_handkeys, \
    keyboard_select_windows_handkeys, keyboard_select_server_handkeys, keyboard_select_visio_handkeys, \
    keyboard_select_project_handkeys, keyboard_cancel_hand_key, keyboard_select_fisic_handkeys
from keyboards.keyboard_admin_add_keys import keyboard_select_category_set_keys, keyboards_list_product_set_keys, \
    keyboards_list_type_office_set_keys, keyboards_list_type_windows_set_keys, keyboards_add_more_keys
from services.googlesheets import get_list_product, get_key_product, get_key_product_office365, append_order,\
    update_row_key_product, get_cost_product, get_info_order, update_row_key_product_new_key, \
    update_row_key_product_cancel, delete_row_order, update_row_order_listkey, get_values_hand_product, set_key_in_sheet

from config_data.config import Config, load_config
from filter.user_filter import check_user
from filter.admin_filter import check_admin
from module.data_base import get_list_users, get_list_admins

from datetime import datetime, timedelta
from datetime import date
from secrets import token_urlsafe
import requests
import logging

config: Config = load_config()
router = Router()
user_dict = {}


class Keys(StatesGroup):
    get_id_order = State()
    get_key_hand = State()
    get_count_hand = State()
    set_key = State()
    set_activate = State()
    get_id_order_cancel = State()


def get_telegram_user(user_id, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    return response.json()


# КЛЮЧ
@router.message(F.text == 'Ключи')
async def process_get_keys(message: Message) -> None:
    logging.info(f'process_get_keys: {message.chat.id}')
    """
    Функция позволяет получить новый ключ или заменить ранее выданный
    :param message:
    :return:
    """
    if check_admin(telegram_id=message.chat.id):
        await message.answer(text="Что требуется сделать с ключом?",
                             reply_markup=keyboard_select_action_keys_admin())
    elif check_user(telegram_id=message.chat.id):
        await message.answer(text="Что требуется сделать с ключом?",
                             reply_markup=keyboard_select_action_keys_manager())



# <editor-fold desc = "СЕКЦИЯ (main keyboard -> [Ключ] -> [Заменить ключ] - change_key)">
# main keyboard -> [Ключ] -> [Заменить]
@router.callback_query(F.data == 'change_key')
async def process_change_keys(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_get_keys: {callback.message.chat.id}')
    await callback.message.answer(text='Пришлите номер заказа для которого нужно заменить ключ')
    await state.set_state(Keys.get_id_order)


# main keyboard -> [Ключ] - [Заменить] - получение номера заказа, выдача ключа того же товара,
# добавления ключа в таблицу продаж как замену
@router.message(F.text, StateFilter(Keys.get_id_order))
async def process_get_id_order(message: Message, state: FSMContext) -> None:
    """
    Функция реализует замену ключа по ранее выполненному заказу
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_get_id_order: {message.chat.id}')
    # получаем информацию о заказе по его токен
    info_order = get_info_order(message.text)
    # если такой заказ найден выводим информацию о нем
    if info_order:
        # print(info_order)
        await message.answer(text=f'№ заказa: {info_order[0]}\n'
                                  f'дата: {info_order[1]}-{info_order[2]}\n'
                                  f'Менеджер: {info_order[3]}\n'
                                  f'Ключ: <code>{info_order[4]}</code>\n'
                                  f'Стоимость: {info_order[5].split(".")[0]} ₽\n'
                                  f'Категория {info_order[6]} - продукт {info_order[7]}',
                             parse_mode='html')
        # переменная для записи нового ключа
        new_key = ''
        # ищем свободный ключ в категории выполненного заказа
        if info_order[6] == 'Office 365':
            # получаем список ключей продукта
            list_key = get_key_product_office365(info_order[6])
            # проходим по всем ключам
            for key in list_key:
                # находим свободный
                if key[1] == '✅':
                    # получаем ключ
                    new_key = key[0]
                    # обновляем значение активации ключа
                    update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
                                           id_key=key[-1], change=True, token_key=info_order[4])
                    # update_row_key_product_cancel(category=info_order[6], key=info_order[4])
                    # останавливаем цикл, так как ключ получен
                    break
        # если категория office или windows здесь поиск сложнее так как есть разные способы выдачи
        elif info_order[6] == 'office' or info_order[6] == 'windows':
            # получаем список ключей продукта по категории и продукту
            list_key = get_key_product(category=info_order[6], product=int(info_order[9]))
            # получаем способ выдачи из выполненного заказа
            type_give = info_order[8]
            # формируем пустые списки для записи в них ключей с разными способами выдачи
            list_key_online = []
            list_key_phone = []
            list_key_linking = []
            # создаем словарь, в который помещены эти списки
            dict_key_office = {
                "list_key_online": list_key_online,
                "list_key_phone": list_key_phone,
                "list_key_linking": list_key_linking
            }
            # наполняем словарь
            key = "list_key_online"
            for i, item in enumerate(list_key[1:]):
                # в таблицу первыми перечислены ключи 'online', поэтому этот ключ первый, далее когда встречаем
                # 'По телефону:' переключаем ключ
                if item[0] == 'По телефону:':
                    key = "list_key_phone"
                # такая же история и с 'С привязкой:'
                if item[0] == 'С привязкой:':
                    key = "list_key_linking"
                dict_key_office[key].append(item)
            # если способ выдачи ключа в заказе
            if type_give == 'online':
                # print(dict_key_office["list_key_phone"])
                for key in dict_key_office["list_key_online"]:
                    if '✅' in key and key[1] != '':
                        new_key = key[1]
                        update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
                                               id_key=key[-1], change=True, token_key=info_order[4])
                        # update_row_key_product_cancel(category=info_order[6], key=info_order[4])
                        break
            if type_give == 'phone':
                # print(dict_key_office["list_key_online"])
                for key in dict_key_office["list_key_phone"]:
                    if '✅' in key and key[1] != '':
                        new_key = key[1]
                        update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
                                               id_key=key[-1], change=True, token_key=info_order[4])
                        # update_row_key_product_cancel(category=info_order[6], key=info_order[4])
                        break
            if type_give == 'linking':
                # print(dict_key_office["list_key_online"])
                for key in dict_key_office["list_key_linking"]:
                    if '✅' in key and key[1] != '':
                        new_key = key[1]
                        update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
                                               id_key=key[-1], change=True, token_key=info_order[4])
                        # update_row_key_product_cancel(category=info_order[6], key=info_order[4])
                        break

        elif info_order[6] == 'visio' or info_order[6] == 'project':
            list_key = get_key_product(category=info_order[6], product=int(info_order[9]))
            for key in list_key:
                if '✅' in key and key[1] != '':
                    new_key = key[1]
                    update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
                                           id_key=key[-1], change=True, token_key=info_order[4])
                    # update_row_key_product_cancel(category=info_order[6], key=info_order[4])
                    break

        await message.answer(text=f'Новый ключ: <code>{new_key}</code>', parse_mode='html')
        # заносим ключ в таблицу заказов
        update_row_key_product_new_key(new_key=new_key, id_order=message.text)

        await state.set_state(default_state)
    else:
        await message.answer(text="Заказ не найден, повторите ввод")
# </editor-fold>


# <editor-fold desc = "СЕКЦИЯ (main keyboard -> [Ключ] -> [Выдать] - get_key)">
# КЛЮЧ - [Выдать] - категории продуктов
@router.callback_query(F.data == 'get_key')
async def process_select_category(callback: CallbackQuery) -> None:
    logging.info(f'process_select_category: {callback.message.chat.id}')
    try:
        await callback.message.edit_text(text='Выберите категорию продукта для получения ключа',
                                         reply_markup=keyboard_select_category_keys())
    except:
        await callback.message.edit_text(text='Выберитe категoрию продукта для получения ключа',
                                         reply_markup=keyboard_select_category_keys())


# КЛЮЧ - [Выдать] - категории - продукты
@router.callback_query(F.data.startswith('getproduct'))
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


# КЛЮЧ - [Выдать] - категории - продукт - способ выдачи (для office и windows)
@router.callback_query(F.data.startswith('typegive_'))
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
@router.callback_query(F.data.startswith('keyproduct_'))
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
        # print(dict_key_office["list_key_phone"])
        for key in dict_key_office["list_key_phone"]:
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
    print(list_key_product)
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
    token_order = str(token_urlsafe(8))
    current_date = datetime.now()
    product_list = product.split()
    product = ' '.join(product_list)
    current_date_string = current_date.strftime('%m/%d/%y %H:%M:%S')
    cost = '/'.join([cost[1], cost[0], cost[2], cost[3]])
    append_order(id_order=token_order, date=current_date_string.split()[0], time=current_date_string.split()[1],
                 username=callback.from_user.username, key=key_product, cost=cost, category=category, product=product,
                 type_give=type_give, id_product=id_product_in_category)
    # key_product_ = key_product
    # if category == 'Office 365':
    #     key_product_ = key_product.split(':')[2]
    await callback.message.answer(text=f'Вы запрашивали:\n'
                                       f'<code>Ключ для {product}\n'
                                       f'{key_product}\n'
                                       f'Номер заказа: {token_order}</code>\n'
                                       f'отправьте его заказчику',
                                  reply_markup=keyboards_cancel_append_key(id_order=token_order),
                                  parse_mode='html')
    update_row_key_product(category=category, id_product_in_category=id_product_in_category, id_key=id_row_key)
    list_admin = get_list_admins()
    for id_admin in list_admin:
        result = get_telegram_user(user_id=id_admin[0], bot_token=config.tg_bot.token)
        if 'result' in result:
            await bot.send_message(chat_id=int(id_admin[0]),
                                   text=f'✅ Менеджер @{callback.from_user.username} преступил к работе')

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



@router.callback_query(F.data.startswith('pageback_'))
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


@router.callback_query(F.data.startswith('cancel_get_key'))
async def process_cancel_get_key(callback: CallbackQuery) -> None:
    logging.info(f'process_cancel_get_key: {callback.message.chat.id}')
    id_order = callback.data.split('#')[1]
    info_order = get_info_order(id_order)
    list_key = info_order[4].split(',')
    # print(list_key)
    for key in list_key:
        update_row_key_product_cancel(category=info_order[6], key=key)
    delete_row_order(id_order=id_order)
    await callback.message.edit_text(text='Активация ключа в таблице восстановлена')


@router.callback_query(F.data.startswith('append_get_key'))
async def process_append_get_key(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    logging.info(f'process_cancel_get_key: {callback.message.chat.id}')
    id_order = callback.data.split('#')[1]
    info_order = get_info_order(id_order)
    if info_order:
        # print(info_order)
        new_key = ''

        if info_order[6] == 'Office 365':
            list_key = get_key_product_office365(info_order[6])
            for key in list_key:
                # print(key)
                if key[1] == '✅':
                    new_key = key[0]
                    update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
                                           id_key=key[-1])
                    count_pos = user_dict[callback.message.chat.id]['count_pos']
                    await state.update_data(count_pos=count_pos - 1)
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
                for key in dict_key_office["list_key_online"]:
                    if '✅' in key and key[1] != '':
                        new_key = key[1]
                        update_row_key_product(category=info_order[6], id_product_in_category=int(info_order[9]),
                                               id_key=key[-1])
                        count_pos = user_dict[callback.message.chat.id]['count_pos']
                        await state.update_data(count_pos=count_pos - 1)
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
                        count_pos = user_dict[callback.message.chat.id]['count_pos']
                        await state.update_data(count_pos=count_pos - 1)
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
        len_key = len(text_old_list)
        if len_key == 5:
            text_old_list[2] = f'1№ {text_old_list[2]}'
        text_old_list.insert(-2, f'{len_key-3}№ {new_key}')
        text_old_list.insert(1, '<code>')
        text_old_list.insert(-1, '</code>')
        text_new = '\n'.join(text_old_list)

        await callback.message.edit_text(text=f'{text_new}',
                                         reply_markup=keyboards_cancel_append_key(id_order=info_order[0]),
                                         parse_mode='html')
        category = info_order[6]
        product = info_order[7]
        type_give = info_order[8]
        if (category in ['office', 'windows'] and type_give == 'online') or \
                (category == 'windows' and type_give == 'linking') or (category == 'Office 365'):
            user_dict[callback.message.chat.id] = await state.get_data()
            count_pos = user_dict[callback.message.chat.id]['count_pos']
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

        list_get_key = [info_order[4]]
        list_get_key.append(new_key)
        # print(list_get_key)
        update_row_order_listkey(id_order=id_order, listkey=','.join(list_get_key))

        if new_key == '':
            await callback.message.answer(text="Ключи выбранного продукта закончились")
# </editor-fold>


# <editor-fold desc = "СЕКЦИЯ (main keyboard -> [Ключ] -> [Отметить продажу] - hand_key)">
# КЛЮЧ - [Отметить продажу] - Категория
@router.callback_query(F.data == 'hand_key')
async def process_hand_keys(callback: CallbackQuery) -> None:
    logging.info(f'process_hand_keys: {callback.message.chat.id}')
    await callback.message.answer(text='Выберите категорию для ручного ввода',
                                  reply_markup=keyboard_select_category_handkeys())


# КЛЮЧ - [Ручной ввод] - Категория - Продукт
@router.callback_query(F.data.startswith('handgetproduct_'))
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
    elif category == 'fisic':
        keyboard = keyboard_select_fisic_handkeys()
    await state.update_data(category_hand=category)
    await callback.message.edit_text(text='Выберите продукт:',
                                     reply_markup=keyboard)


# КЛЮЧ - [Ручной ввод] - Физический продукт - Продукт - Указать количество
async def process_input_fisic(message: Message, state: FSMContext):
    logging.info(f'process_input_fisic: {message.chat.id}')
    user_dict[message.chat.id] = await state.get_data()
    product_hand = user_dict[message.chat.id]['product_hand']
    await message.answer(text=f'Укажите количество выдаваемого продукта {product_hand}')
    await state.set_state(Keys.get_count_hand)


# КЛЮЧ - [Ручной ввод] - Категория - Продукт - Добавление физического продукта
@router.message(StateFilter(Keys.get_count_hand), lambda x: x.text.isdigit() and 1 <= int(x.text))
async def process_hand_set_product(message: Message, state: FSMContext) -> None:
    logging.info(f'process_hand_set_product: {message.chat.id}')
    user_dict[message.chat.id] = await state.get_data()
    token_order = str(token_urlsafe(8))
    current_date = datetime.now()
    current_date_string = current_date.strftime('%m/%d/%y %H:%M:%S')
    count_key = ','.join(['физический продукт'] * int(message.text))
    append_order(id_order=token_order,
                 date=current_date_string.split()[0],
                 time=current_date_string.split()[1],
                 username=message.chat.username,
                 key=count_key,
                 cost=user_dict[message.chat.id]['cost_hand'],
                 category=user_dict[message.chat.id]['category_hand'],
                 product=user_dict[message.chat.id]['product_hand'],
                 type_give='hand',
                 id_product='-')
    await message.answer(text=f'Ключ добавлен в таблицу заказов')
    await state.set_state(default_state)


# КЛЮЧ - [Ручной ввод] - Категория - Продукт - Добавить ключ
@router.callback_query(F.data.startswith('handgetkey'))
async def process_hand_keys_product(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_hand_keys_product: {callback.message.chat.id}')
    # category = callback.data.split('#')[1]
    product = callback.data.split('#')[1]
    # print(product, callback.message)
    cost_hand_list = get_values_hand_product(product)
    print(cost_hand_list)
    cost_hand = f'{cost_hand_list[1]}/{cost_hand_list[0]}/{cost_hand_list[2]}/{cost_hand_list[3]}'
    await state.update_data(cost_hand=cost_hand)
    await state.update_data(product_hand=product)
    if product in ['USB флешка Windows 10/11', 'Windows 10 Pro OEM - Наклейка', 'Windows 11 Pro OEM - Наклейка',
                   'Microsoft Windows 10 PRO (BOX)', 'Office 2019 POS (карта)']:
        await process_input_fisic(message=callback.message, state=state)
    else:
        await callback.message.answer(text=f'Пришлите ключ для добавления',
                                      reply_markup=keyboard_cancel_hand_key())
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
    await message.answer(text=f'Ключ добавлен в таблицу заказов')
    await state.set_state(default_state)


@router.callback_query(F.data == 'cancel_hand_key')
async def process_hand_keys_product_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_hand_keys_product_cancel: {callback.message.chat.id}')
    await callback.message.answer('Добавление ключа вручную отменено')
    await state.set_state(default_state)
# </editor-fold>


# <editor-fold desc = "СЕКЦИЯ (main keyboard -> [Ключ] -> [Отменить продажу] - change_key)">
# main keyboard -> [Ключ] -> [Отменить]
@router.callback_query(F.data == 'cancel_key')
async def process_cancel_keys(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_cancel_keys: {callback.message.chat.id}')
    # await callback.message.answer(text='Функционал "Отмены выданного ключа" в разработке')
    await callback.message.answer(text='Пришлите номер заказа, который нужно отменить')
    await state.set_state(Keys.get_id_order_cancel)


@router.message(F.text, StateFilter(Keys.get_id_order_cancel))
async def process_get_id_order_cancel_keys(message: Message, state: FSMContext) -> None:
    """
    Функция реализует замену ключа по ранее выполненному заказу
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_get_id_order_cancel_keys: {message.chat.id}')
    # получаем информацию о заказе по его токен
    info_order = get_info_order(message.text)
    # если такой заказ найден выводим информацию о нем
    if info_order:
        # print(info_order)
        await message.answer(text=f'№ заказa: {info_order[0]}\n'
                                  f'дата: {info_order[1]}-{info_order[2]}\n'
                                  f'Менеджер: {info_order[3]}\n'
                                  f'Ключ: <code>{info_order[4]}</code>\n'
                                  f'Стоимость: {info_order[5].split(".")[0]} ₽\n'
                                  f'Категория {info_order[6]} - продукт {info_order[7]}',
                             parse_mode='html')
        # получаем текущую дату
        current_date = datetime.now()
        # преобразуем ее в строку
        period_start = current_date.strftime('%m/%d/%y')
        list_date_start = period_start.split('/')
        date_start = date(int(list_date_start[2]), int(list_date_start[0]), int(list_date_start[1]))
        today = datetime.now()
        tomorrow = today - timedelta(days=7)
        period_finish = tomorrow.strftime('%m/%d/%y')
        list_date_finish = period_finish.split('/')
        date_finish = date(int(list_date_finish[2]), int(list_date_finish[0]), int(list_date_finish[1]))
        list_date_order = info_order[1].split('/')
        date_order = date(int(list_date_order[2]), int(list_date_order[0]), int(list_date_order[1]))
        if date_finish <= date_order <= date_start:
            await message.answer(text='Ключ выдан менее 7 дней назад. Отменить его выдачу?',
                                 reply_markup=keyboards_cancel_get_key(id_order=info_order[0]))
        else:
            await message.answer(text='❌с момента выдачи ключа прошло более 7 дней')

# </editor-fold>



# <editor-fold desc = "СЕКЦИЯ (main keyboard -> [Ключ] -> [Добавить] - add_key)">
# main keyboard -> [Ключ] -> [Добавить]
@router.callback_query(F.data == 'add_key')
async def process_add_keys(callback: CallbackQuery) -> None:
    logging.info(f'process_add_keys: {callback.message.chat.id}')
    # await callback.message.answer(text='Функционал "Добавления ключей в таблицу" в разработке')
    try:
        await callback.message.edit_text(text='Выберите категорию продукта для добавления ключа',
                                         reply_markup=keyboard_select_category_set_keys())
    except:
        await callback.message.edit_text(text='Выберитe категoрию продукта для добавления ключа',
                                         reply_markup=keyboard_select_category_set_keys())


# КЛЮЧ - [Добавить] - категории - продукты
@router.callback_query(F.data.startswith('setproduct'))
async def process_select_product_set_keys(callback: CallbackQuery) -> None:
    logging.info(f'process_select_product_set_keys:{callback.data.split("_")[1]} {callback.message.chat.id} ')
    list_product = get_list_product(callback.data.split('_')[1])

    if callback.data.split('_')[1] == 'windows':
        list_product = list_product[:2]
    if callback.data.split('_')[1] == 'office':
        list_product = list_product[:3]
    try:
        await callback.message.answer(text='Выберите продукт для добавления ключа.',
                                      reply_markup=keyboards_list_product_set_keys(list_product=list_product,
                                                                                   category=callback.data.split('_')[1]))
    except:
        await callback.message.answer(text='Выберите прoдукт для добавления ключа',
                                      reply_markup=keyboards_list_product_set_keys(list_product=list_product,
                                                                                   category=callback.data.split('_')[1]))


# КЛЮЧ - [Выдать] - категории - продукт - способ выдачи (для office и windows)
@router.callback_query(F.data.startswith('settypegive_'))
async def process_select_typegive_set_keys(callback: CallbackQuery) -> None:
    logging.info(f'process_select_typegive_set_keys: {callback.message.chat.id}')
    # получаем наименование категории
    category = callback.data.split('_')[1].split(':')[0]
    # номер продукта в категории
    id_product_in_category = int(callback.data.split('_')[1].split(':')[1])
    if category == 'office':
        await callback.message.answer(text=f'Для добавления ключа, выберите способ его выдачи:',
                                      reply_markup=keyboards_list_type_office_set_keys(category=category,
                                                                                       product=id_product_in_category))
    elif category == 'windows':
        await callback.message.answer(text=f'Для добавления ключа, выберите способ его выдачи:',
                                      reply_markup=keyboards_list_type_windows_set_keys(category=category,
                                                                                        product=id_product_in_category))


# КЛЮЧ - [Выдать] - категории - продукт - key
@router.callback_query(F.data.startswith('setkeyproduct_'))
async def process_set_key_product(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_set_key_product: {callback.message.chat.id}')
    await callback.message.answer(text='Пришлите ключ для добавления')

    category = callback.data.split('_')[1].split(':')[0]
    if category == 'office' or category == 'windows':
        type_give = callback.data.split('_')[1].split(':')[2]
        await state.update_data(type_give_set=type_give)
    id_product_in_category = int(callback.data.split('_')[1].split(':')[1])
    await state.update_data(category_set=category)
    await state.update_data(id_product_in_category_set=id_product_in_category)

    await state.set_state(Keys.set_key)


@router.message(F.text, StateFilter(Keys.set_key))
async def process_set_key_product(message: Message, state: FSMContext) -> None:
    logging.info(f'process_set_key_product: {message.chat.id}')
    set_key = message.text
    await state.update_data(set_key=set_key)
    user_dict[message.chat.id] = await state.update_data()
    category = user_dict[message.chat.id]['category_set']
    if category != 'Office 365':
        await message.answer(text='Пришлите количество активаций для ключа:')
        await state.set_state(Keys.set_activate)
    else:
        await process_set_key_office365(message=message, state=state)


@router.message(F.text, StateFilter(Keys.set_activate))
async def process_set_key_product(message: Message, state: FSMContext) -> None:
    logging.info(f'process_set_key_product: {message.chat.id}')
    await state.set_state(default_state)
    await state.update_data(set_activate=int(message.text))
    user_dict[message.chat.id] = await state.update_data()
    category = user_dict[message.chat.id]['category_set']
    # id_product_in_category = user_dict[message.chat.id]['id_product_in_category_set']

    if category == 'office':
        await process_set_key_office(message=message, state=state)
    elif category == 'windows':
        await process_set_key_windows(message=message, state=state)
    elif category == 'visio' or category == 'project':
        await process_set_key_visio_and_project(message=message, state=state)


async def process_set_key_office(message: Message, state: FSMContext):
    logging.info(f'process_set_key_office: {message.chat.id}')
    user_dict[message.chat.id] = await state.update_data()
    category = user_dict[message.chat.id]['category_set']
    id_product_in_category = user_dict[message.chat.id]['id_product_in_category_set']
    set_key = user_dict[message.chat.id]['set_key']
    set_activate = user_dict[message.chat.id]['set_activate']
    list_key_product = get_key_product(category=category, product=id_product_in_category)

    list_key_online = []
    list_key_phone = []
    list_key_linkingMS = []
    dict_key_office = {
        "onlineoffice": list_key_online,
        "phoneoffice": list_key_phone,
        "linkingMSoffice": list_key_linkingMS
    }

    key = "onlineoffice"
    for i, item in enumerate(list_key_product[1:]):
        if item[0] == 'По телефону:':
            key = "phoneoffice"
        if item[0] == 'С привязкой:':
            key = "linkingMSoffice"
        dict_key_office[key].append(item)

    type_give = user_dict[message.chat.id]['type_give_set']
    if type_give == 'onlineoffice':
        for key_info in dict_key_office[type_give]:
            if key_info[1] == '' and 'Office' in key_info[0]:
                set_key_in_sheet(category=category, id_product_in_category=id_product_in_category,
                                 id_key=int(key_info[-1]), set_key=set_key, activate=set_activate)
                await message.answer(text='Ключ добавлен в таблицу',
                                     reply_markup=keyboards_add_more_keys())
                break
        else:
            await message.answer(text='Добавьте строки для добавления ключей в таблицу')

    elif type_give == 'phoneoffice':
        for key_info in dict_key_office[type_give]:
            if key_info[1] == '' and 'Office' in key_info[0]:
                set_key_in_sheet(category=category, id_product_in_category=id_product_in_category,
                                 id_key=int(key_info[-1]), set_key=set_key, activate=set_activate)
                await message.answer(text='Ключ добавлен в таблицу',
                                     reply_markup=keyboards_add_more_keys())
                break
        else:
            await message.answer(text='Добавьте строки для добавления ключей в таблицу')

    elif type_give == 'linkingMSoffice':
        for key_info in dict_key_office[type_give]:
            if key_info[1] == '' and 'Office' in key_info[0]:
                set_key_in_sheet(category=category, id_product_in_category=id_product_in_category,
                                 id_key=int(key_info[-1]), set_key=set_key, activate=set_activate)
                await message.answer(text='Ключ добавлен в таблицу',
                                     reply_markup=keyboards_add_more_keys())
                break
        else:
            await message.answer(text='Добавьте строки для добавления ключей в таблицу')


@router.callback_query(F.data == 'add_more_keys')
async def process_add_more_keys(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_add_more_keys: {callback.message.chat.id}')
    await callback.message.answer(text='Пришлите ключ для добавления')
    await state.set_state(Keys.set_key)


async def process_set_key_windows(message: Message, state: FSMContext):
    logging.info(f'process_set_key_windows: {message.chat.id}')
    user_dict[message.chat.id] = await state.update_data()
    category = user_dict[message.chat.id]['category_set']
    id_product_in_category = user_dict[message.chat.id]['id_product_in_category_set']
    set_key = user_dict[message.chat.id]['set_key']
    set_activate = user_dict[message.chat.id]['set_activate']
    list_key_product = get_key_product(category=category, product=id_product_in_category)

    list_key_online = []
    list_key_phone = []
    list_key_linking = []
    dict_key_windows = {
        "onlinewindows": list_key_online,
        "phonewindows": list_key_phone,
        "linkingwindows": list_key_linking
    }
    key = "onlinewindows"
    for i, item in enumerate(list_key_product[1:]):
        if item[0] == 'По телефону:':
            key = "phonewindows"
        if item[0] == 'С привязкой:':
            key = "linkingwindows"

        dict_key_windows[key].append(item)

    type_give = user_dict[message.chat.id]['type_give_set']
    if type_give == 'onlinewindows':
        for key_info in dict_key_windows[type_give]:
            if key_info[1] == '' and 'Windows' in key_info[0]:
                set_key_in_sheet(category=category, id_product_in_category=id_product_in_category,
                                 id_key=int(key_info[-1]), set_key=set_key, activate=set_activate)
                await message.answer(text='Ключ добавлен в таблицу',
                                     reply_markup=keyboards_add_more_keys())
                break
        else:
            await message.answer(text='Добавьте строки для добавления ключей в таблицу')

    elif type_give == 'phonewindows':
        for key_info in dict_key_windows[type_give]:
            if key_info[1] == '' and 'Windows' in key_info[0]:
                set_key_in_sheet(category=category, id_product_in_category=id_product_in_category,
                                 id_key=int(key_info[-1]), set_key=set_key, activate=set_activate)
                await message.answer(text='Ключ добавлен в таблицу',
                                     reply_markup=keyboards_add_more_keys())
                break
        else:
            await message.answer(text='Добавьте строки для добавления ключей в таблицу')

    elif type_give == 'linkingwindows':
        for key_info in dict_key_windows[type_give]:
            if key_info[1] == '' and 'Windows' in key_info[0]:
                set_key_in_sheet(category=category, id_product_in_category=id_product_in_category,
                                 id_key=int(key_info[-1]), set_key=set_key, activate=set_activate)
                await message.answer(text='Ключ добавлен в таблицу',
                                     reply_markup=keyboards_add_more_keys())
                break
        else:
            await message.answer(text='Добавьте строки для добавления ключей в таблицу')


async def process_set_key_office365(message: Message, state: FSMContext):
    logging.info(f'process_select_key_office365: {message.chat.id}')
    user_dict[message.chat.id] = await state.update_data()
    category = user_dict[message.chat.id]['category_set']
    id_product_in_category = user_dict[message.chat.id]['id_product_in_category_set']
    set_key = user_dict[message.chat.id]['set_key']
    list_key_product = get_key_product_office365(category=category)

    for key_info in list_key_product:
        if key_info[0] == '':
            set_key_in_sheet(category=category, id_product_in_category=id_product_in_category,
                             id_key=int(key_info[-1]), set_key=set_key, activate=1)
            await message.answer(text='Ключ добавлен в таблицу',
                                 reply_markup=keyboards_add_more_keys())
            break
    else:
        await message.answer(text='Добавьте строки для добавления ключей в таблицу')


async def process_set_key_visio_and_project(message: Message, state: FSMContext):
    logging.info(f'process_set_key_visio_and_project: {message.chat.id}')
    user_dict[message.chat.id] = await state.update_data()
    category = user_dict[message.chat.id]['category_set']
    id_product_in_category = user_dict[message.chat.id]['id_product_in_category_set']
    set_key = user_dict[message.chat.id]['set_key']
    set_activate = user_dict[message.chat.id]['set_activate']
    # получаем список ключей в таблице во вкладке категории и в столбце продукта
    list_key_product = get_key_product(category=category, product=id_product_in_category)[1:]
    for key_info in list_key_product:
        if key_info[1] == '' and ('Visio' in key_info[0] or 'Project' in key_info[0]):
            set_key_in_sheet(category=category, id_product_in_category=id_product_in_category,
                             id_key=int(key_info[-1]), set_key=set_key, activate=set_activate)
            await message.answer(text='Ключ добавлен в таблицу',
                                 reply_markup=keyboards_add_more_keys())
            break
    else:
        await message.answer(text='Добавьте строки для добавления ключей в таблицу')


@router.callback_query(F.data.startswith('setpageback_'))
async def process_select_back(callback: CallbackQuery) -> None:
    logging.info(f'process_select_back: {callback.message.chat.id}')
    back = callback.data.split('_')[1]
    if back == 'category':
        await process_add_keys(callback)
    elif back == 'setproductoffice':
        logging.info(f'process_select_productoffice: {callback.message.chat.id}')
        list_product = get_list_product('office')
        await callback.message.edit_text(text='Выберите прoдукт для добавления ключа',
                                         reply_markup=keyboards_list_product_set_keys(list_product=list_product,
                                                                                      category='office'))
    elif back == 'setproductwindows':
        logging.info(f'process_select_productwindows: {callback.message.chat.id}')
        list_product = get_list_product('windows')
        await callback.message.edit_text(text='Выберите прoдукт для добавления ключа',
                                         reply_markup=keyboards_list_product_set_keys(list_product=list_product,
                                                                                      category='windows'))
# </editor-fold>
