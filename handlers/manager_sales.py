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
from datetime import date

from keyboards.keyboard_sales import keyboard_select_period_sales, keyboard_select_scale_sales, keyboards_list_product_sales
from filter.user_filter import check_user
from filter.admin_filter import chek_admin
from services.googlesheets import get_list_orders


router = Router()
class Sales(StatesGroup):
    period = State()
user_dict = {}


# Статитстика - период статистики
@router.message(F.text == 'Отчет по продажам', lambda message: check_user(message.chat.id))
async def process_get_statistic_salesperiod(message: Message) -> None:
    logging.info(f'process_get_statistic_salesperiod: {message.chat.id}')
    await message.answer(text="Выберите период для получения отчета о продажах",
                         reply_markup=keyboard_select_period_sales())


# Статистика - компания или менеджер для админа и менеджер для менеджера
@router.callback_query(F.data.startswith('salesperiod'), lambda callback: check_user(callback.message.chat.id))
async def process_get_salesscale(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_get_salesscale: {callback.message.chat.id}')
    await state.update_data(salesperiod=callback.data.split('_')[1])
    if chek_admin(callback.message.chat.id):
        await callback.message.answer(text='Получить отчет о продажах',
                                      reply_markup=keyboard_select_scale_sales())
    elif check_user(callback.message.chat.id):
        list_username = get_list_users()
        await callback.message.answer(text='Для кого требуется получить отчет о продажах',
                                      reply_markup=keyboards_list_product_sales(list_manager=list_username))


# Статистика - менеджер
@router.callback_query(F.data == 'salesmanager', lambda callback: check_user(callback.message.chat.id))
async def process_get_stat_salesmanager(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_get_stat_salesmanager: {callback.message.chat.id}')
    list_username = get_list_users()
    await callback.message.answer(text='Для кого требуется получить отчет о продажах',
                                  reply_markup=keyboards_list_product_sales(list_manager=list_username))


# Статистика - для выбранного менеджера
@router.callback_query(F.data.startswith('salesmanager#'), lambda callback: check_user(callback.message.chat.id))
async def process_get_stat_select_salesmanager(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_get_stat_select_salesmanager: {callback.message.chat.id}')
    user_name_manager = callback.data.split('#')[1]
    print(user_name_manager)
    user_dict[callback.message.chat.id] = await state.update_data()
    period = int(user_dict[callback.message.chat.id]['salesperiod'])
    list_orders = get_list_orders()
    print(list_orders)
    count = 0
    current_date = datetime.now()
    date1 = current_date.strftime('%m/%d/%y')
    list_date1 = date1.split('/')
    date1 = date(int(list_date1[2]), int(list_date1[0]), int(list_date1[1]))
    text = ''
    dict_order_product = {}
    num = 0
    num_mes = 0
    list_text = []
    for order in list_orders[1:]:
        print(order)
        if user_name_manager in order:
            list_date2 = order[1].split('/')
            date2 = date(int(list_date2[2]), int(list_date2[0]), int(list_date2[1]))
            delta = (date1 - date2).days
            print(delta)
            if delta < period:
                product_list = order[7].split()
                product = ' '.join(product_list)
                if not product in dict_order_product.keys():
                    dict_order_product[product] = 0
                print(order[5])
                num += 1
                num_mes += 1
                dict_order_product[product] += 1
                count += int(order[5].split('.')[0])
                text += f"{num}) Номер заказа: {order[0]} от {order[1]} менеджер {order[3]} стоимость {order[5]}\n"
                if num_mes > 39:
                    num_mes = 0
                    list_text.append(text)
                    text = ''
    list_text.append(text)
    if list_text:
        for text_message in list_text:
            await callback.message.answer(text=f'<b>Отчет о продажах компании:</b>\n'
                                               f'{text_message}\n\n',
                                          parse_mode='html')
    else:
        await callback.message.answer(text=f'<b>Отчет о продаж компании:</b>\n'
                                           f'{text}\n\n',
                                      parse_mode='html')
    total_text = ''
    total_order = 0
    for key_product, value_product in dict_order_product.items():
        total_text += f'<b>{key_product}:</b> {value_product}\n'
        total_order += value_product
    await callback.message.answer(text=f'{total_text}'
                                       f'\n'
                                       f'Менеджер выполнил заказов на {count} ₽\n'
                                       f'Количество продаж: {total_order} шт.',
                                  parse_mode='html')


# Статистика - для выбранного менеджера
@router.callback_query(F.data == 'salescompany', lambda callback: check_user(callback.message.chat.id))
async def process_get_stat_select_salescompany(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_get_stat_select_salescompany: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.update_data()
    period = int(user_dict[callback.message.chat.id]['salesperiod'])
    list_orders = get_list_orders()
    print(list_orders)
    count = 0
    current_date = datetime.now()
    date1 = current_date.strftime('%m/%d/%y')
    list_date1 = date1.split('/')
    date1 = date(int(list_date1[2]), int(list_date1[0]), int(list_date1[1]))
    text = ''
    dict_order_product = {}
    num = 0
    num_mes = 0
    list_text = []
    for order in list_orders[1:]:
        print(order)
        list_date2 = order[1].split('/')
        date2 = date(int(list_date2[2]), int(list_date2[0]), int(list_date2[1]))
        delta = (date1 - date2).days
        print(delta)
        if delta < period:
            product_list = order[7].split()
            product = ' '.join(product_list)
            if not product in dict_order_product.keys():
                dict_order_product[product] = 0
            print(order[5])
            num += 1
            num_mes += 1
            dict_order_product[product] += 1
            count += int(order[5].split('.')[0])
            text += f"{num}) Номер заказа: {order[0]} от {order[1]} менеджер {order[3]} стоимость {order[5]}\n"
            if num_mes > 39:
                num_mes = 0
                list_text.append(text)
                text = ''
    list_text.append(text)
    if list_text:
        for text_message in list_text:
            await callback.message.answer(text=f'<b>Отчет о продажах компании:</b>\n'
                                               f'{text_message}\n\n',
                                          parse_mode='html')
    else:
        await callback.message.answer(text=f'<b>Отчет о продаж компании:</b>\n'
                                           f'{text}\n\n',
                                      parse_mode='html')
    total_text = ''
    total_order = 0
    for key_product, value_product in dict_order_product.items():
        total_text += f'<b>{key_product}:</b> {value_product}\n'
        total_order += value_product
    await callback.message.answer(text=f'{total_text}'
                                       f'\n'
                                       f'Компания выполнила заказов на {count} ₽\n'
                                       f'Количество продаж: {total_order} шт.',
                                  parse_mode='html')