from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter
import logging
from secrets import token_urlsafe
import asyncio
from module.data_base import add_token, get_list_users, get_user, delete_user
from datetime import datetime, timedelta
from datetime import date

import aiogram_calendar
from aiogram.filters.callback_data import CallbackData

from keyboards.keyboard_sales import keyboard_select_period_sales_new, keyboard_select_scale_sales, keyboards_list_product_sales
from filter.user_filter import check_user
from filter.admin_filter import chek_admin
from services.googlesheets import get_list_orders


router = Router()
class Sales(StatesGroup):
    period = State()
    period_start = State()
    period_finish = State()

user_dict = {}


# ПРОДАЖИ - период статистики
@router.message(F.text == 'Отчет по продажам', lambda message: check_user(message.chat.id))
async def process_get_statistic_salesperiod(message: Message) -> None:
    """
    Начало цепочки сообщений для выбора отчета о продажах (выбор периода для которого выдается отчет о продажах)
    Администратор - может выбрать отчет за менеджера или компанию
    Менеджер - может посмотреть отчеты только за менеджеров
    :param message:
    :return:
    """
    logging.info(f'process_get_statistic_salesperiod: {message.chat.id}')
    await message.answer(text="Выберите период для получения отчета о продажах",
                         reply_markup=keyboard_select_period_sales_new())


# календарь
@router.callback_query(F.data == 'salesperiod_calendar')
async def process_buttons_press_start(callback: CallbackQuery, state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2024, 1, 1), datetime(2028, 12, 31))
    # получаем текущую дату
    current_date = datetime.now()
    # преобразуем ее в строку
    date1 = current_date.strftime('%m/%d/%y')
    # преобразуем дату в список
    list_date1 = date1.split('/')
    await callback.message.answer(
        "Выберите начало периода, для получения отчета:",
        reply_markup=await calendar.start_calendar(year=int('20'+list_date1[2]), month=int(list_date1[0]))
    )
    await state.set_state(Sales.period_start)

async def process_buttons_press_finish(callback: CallbackQuery, state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2024, 1, 1), datetime(2028, 12, 31))
    # получаем текущую дату
    current_date = datetime.now()
    # преобразуем ее в строку
    date1 = current_date.strftime('%m/%d/%y')
    # преобразуем дату в список
    list_date1 = date1.split('/')
    await callback.message.answer(
        "Выберите конец периода, для получения отчета:",
        reply_markup=await calendar.start_calendar(year=int('20'+list_date1[2]), month=int(list_date1[0]))
    )
    await state.set_state(Sales.period_finish)


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(Sales.period_start))
async def process_simple_calendar_start(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.edit_text(
            f'Начало периода {date.strftime("%d/%m/%y")}')
        await state.update_data(period_start=date.strftime("%m/%d/%y"))
    await process_buttons_press_finish(callback_query, state=state)


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(Sales.period_finish))
async def process_simple_calendar_finish(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback, callback_data)
    if selected:
        await callback.message.edit_text(
            f'Конец периода {date.strftime("%d/%m/%y")}')
        await state.update_data(period_finish=date.strftime("%m/%d/%y"))
        await state.update_data(salesperiod=0)
    await state.set_state(default_state)
    if chek_admin(callback.message.chat.id):
        await callback.message.answer(text='Получить отчет о продажах',
                                      reply_markup=keyboard_select_scale_sales())
    elif check_user(callback.message.chat.id):
        list_username = get_list_users()
        await callback.message.answer(text='Для кого требуется получить отчет о продажах',
                                      reply_markup=keyboards_list_product_sales(list_manager=list_username))


# ПРОДАЖИ - компания или менеджер для админа и менеджер для менеджера
@router.callback_query(F.data == 'salesperiod_1', lambda callback: check_user(callback.message.chat.id))
async def process_get_salesscale(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Выбор менеджера или компании - для администратора
    Выбор менеджера - для менеджера
    :param callback: salesperiod_{1,7,30}
    :param state:
    :return:
    """
    logging.info(f'process_get_salesscale: {callback.message.chat.id}')
    await state.update_data(salesperiod=callback.data.split('_')[1])
    if chek_admin(callback.message.chat.id):
        await callback.message.answer(text='Получить отчет о продажах',
                                      reply_markup=keyboard_select_scale_sales())
    elif check_user(callback.message.chat.id):
        list_username = get_list_users()
        await callback.message.answer(text='Для кого требуется получить отчет о продажах',
                                      reply_markup=keyboards_list_product_sales(list_manager=list_username))


# ПРОДАЖИ - менеджер
@router.callback_query(F.data == 'salesmanager', lambda callback: check_user(callback.message.chat.id))
async def process_get_stat_salesmanager(callback: CallbackQuery) -> None:
    """
    Выбор менеджера из списка (клавиатура) для которого требуется получить отчет
    :param callback:
    :return:
    """
    logging.info(f'process_get_stat_salesmanager: {callback.message.chat.id}')
    list_username = get_list_users()
    await callback.message.answer(text='Для кого требуется получить отчет о продажах',
                                  reply_markup=keyboards_list_product_sales(list_manager=list_username))


# ПРОДАЖИ - для выбранного менеджера
@router.callback_query(F.data.startswith('salesmanager#'), lambda callback: check_user(callback.message.chat.id))
async def process_get_stat_select_salesmanager(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Формирование отчета о продажах выбранного менеджера за выбранный период
    :param callback: salesmanager#{{manager[1]}:username}
    :param state:
    :return:
    """
    logging.info(f'process_get_stat_select_salesmanager: {callback.message.chat.id}')
    # получаем username менеджера
    user_name_manager = callback.data.split('#')[1]
    # обновляем данные словаря
    user_dict[callback.message.chat.id] = await state.update_data()
    # получаем период для которого нужно получить отчет
    if int(user_dict[callback.message.chat.id]['salesperiod']):
        # получаем текущую дату
        current_date = datetime.now()
        # преобразуем ее в строку
        period_start = current_date.strftime('%m/%d/%y')
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        period_finish = tomorrow.strftime('%m/%d/%y')
        print(period_start, period_finish)
        list_date_start = period_start.split('/')
        date_start = date(int(list_date_start[2]), int(list_date_start[0]), int(list_date_start[1]))
        list_date_finish = period_finish.split('/')
        date_finish = date(int(list_date_finish[2]), int(list_date_finish[0]), int(list_date_finish[1]))
    else:
        period_start = user_dict[callback.message.chat.id]['period_start']
        period_finish = user_dict[callback.message.chat.id]['period_finish']
        print(period_start, period_finish)
        list_date_start = period_start.split('/')
        date_start = date(int(list_date_start[2]), int(list_date_start[0]), int(list_date_start[1]))
        list_date_finish = period_finish.split('/')
        date_finish = date(int(list_date_finish[2]), int(list_date_finish[0]), int(list_date_finish[1]))
    # получаем весь список заказов
    list_orders = get_list_orders()
    # инициализируем счетчик стоимости выполненных заказов
    count = 0
    # инициализируем пременную для списка заказов
    text = ''
    # инициализируем словарь для суммирования количества по продуктам
    dict_order_product = {}
    # переменная для нумерации заказов
    num = 0
    # переменная ограничивающая длину сообщения
    num_mes = 0
    # список выполненых заказов
    list_text = []
    # проходимся по всему списку заказов
    for order in list_orders[1:]:
        # отбираем заказы выполненные выбранным менеджером
        if user_name_manager in order:
            # разбиваем дату выполнения заказа
            list_date_order = order[1].split('/')
            date_order = date(int(list_date_order[2]), int(list_date_order[0]), int(list_date_order[1]))
            # если дата выполнения заказа находится в периоде для предоставления отчета
            if date_start <= date_order and date_order <= date_finish:
                # убираем пробелы слева и справа у продукта
                product_list = order[7].split()
                product = ' '.join(product_list)
                # если ключа с таким продуктом в словаре еще нет, то создаем его и инициализируем значение ключа 0
                if not product in dict_order_product.keys():
                    dict_order_product[product] = 0
                # увеличиваем счетчик выполненных заказов
                num += 1
                # увеличиваем счетчик для ограничения длины сообщения
                num_mes += 1
                # увеличиваем счетчик количество проданных продуктов в словаре
                dict_order_product[product] += 1
                # увеличиваем сумму выполненных заказов
                count += int(order[5].split('.')[0])
                # формируем строку для вывода в сообщении
                text += f"{num}) Номер заказа: {order[0]} от {order[1]} менеджер {order[3]} стоимость {order[5]}\n"
                # проверяем длину сообщения
                if num_mes > 39:
                    # обнуляем длину сообщения
                    num_mes = 0
                    # добавляем сформированную строку в список для сообщения
                    list_text.append(text)
                    # обнуляем строку
                    text = ''
    # добавляем строки с заказами для последнего сообщения
    list_text.append(text)
    # если список с заказами не пустой
    if list_text:
        # то отправляем сообщения с выполненными заказами
        for text_message in list_text:
            await callback.message.answer(text=f'<b>Отчет о продажах менеджера:</b>\n'
                                               f'{text_message}\n\n',
                                          parse_mode='html')
    else:
        # выводим пустую строку
        await callback.message.answer(text=f'<b>Отчет о продажах менеджера:</b>\n'
                                           f'{text}\n\n',
                                      parse_mode='html')
    # инициализируем переменную для сообщения для итоговых данных
    total_text = ''
    # количество проданных продуктов
    total_order = 0
    # проходим по сформированному словарю и получаем ключ: продукт и значение: количество проданных продуктов
    for key_product, value_product in dict_order_product.items():
        # информация по продукту
        total_text += f'<b>{key_product}:</b> {value_product}\n'
        # общее количество продаж
        total_order += value_product
    await callback.message.answer(text=f'{total_text}'
                                       f'\n'
                                       f'Менеджер выполнил заказов на {count} ₽\n'
                                       f'Количество продаж: {total_order} шт.',
                                  parse_mode='html')


# ПРОДАЖИ - для всей компании
@router.callback_query(F.data == 'salescompany', lambda callback: check_user(callback.message.chat.id))
async def process_get_stat_select_salescompany(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_get_stat_select_salescompany: {callback.message.chat.id}')
    # обновляем данные словаря
    user_dict[callback.message.chat.id] = await state.update_data()
    # получаем период для которого нужно получить отчет
    if int(user_dict[callback.message.chat.id]['salesperiod']):
        # получаем текущую дату
        current_date = datetime.now()
        # преобразуем ее в строку
        period_start = current_date.strftime('%m/%d/%y')
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        period_finish = tomorrow.strftime('%m/%d/%y')
        print(period_start, period_finish)
        list_date_start = period_start.split('/')
        date_start = date(int(list_date_start[2]), int(list_date_start[0]), int(list_date_start[1]))
        list_date_finish = period_finish.split('/')
        date_finish = date(int(list_date_finish[2]), int(list_date_finish[0]), int(list_date_finish[1]))
    else:
        period_start = user_dict[callback.message.chat.id]['period_start']
        period_finish = user_dict[callback.message.chat.id]['period_finish']
        print(period_start, period_finish)
        list_date_start = period_start.split('/')
        date_start = date(int(list_date_start[2]), int(list_date_start[0]), int(list_date_start[1]))
        list_date_finish = period_finish.split('/')
        date_finish = date(int(list_date_finish[2]), int(list_date_finish[0]), int(list_date_finish[1]))
    # получаем весь список заказов
    list_orders = get_list_orders()
    # инициализируем счетчик стоимости выполненных заказов
    count = 0
    # инициализируем пременную для списка заказов
    text = ''
    # инициализируем словарь для суммирования количества по продуктам
    dict_order_product = {}
    # переменная для нумерации заказов
    num = 0
    # переменная ограничивающая длину сообщения
    num_mes = 0
    # список выполненых заказов
    list_text = []
    # проходимся по всему списку заказов
    for order in list_orders[1:]:
        # разбиваем дату выполнения заказа
        list_date_order = order[1].split('/')
        date_order = date(int(list_date_order[2]), int(list_date_order[0]), int(list_date_order[1]))
        # если дата выполнения заказа находится в периоде для предоставления отчета
        if date_start <= date_order and date_order <= date_finish:
            # убираем пробелы слева и справа у продукта
            product_list = order[7].split()
            product = ' '.join(product_list)
            # если ключа с таким продуктом в словаре еще нет, то создаем его и инициализируем значение ключа 0
            if not product in dict_order_product.keys():
                dict_order_product[product] = 0
            # увеличиваем счетчик выполненных заказов
            num += 1
            # увеличиваем счетчик для ограничения длины сообщения
            num_mes += 1
            # увеличиваем счетчик количество проданных продуктов в словаре
            dict_order_product[product] += 1
            # увеличиваем сумму выполненных заказов
            count += int(order[5].split('.')[0])
            # формируем строку для вывода в сообщении
            text += f"{num}) Номер заказа: {order[0]} от {order[1]} менеджер {order[3]} стоимость {order[5]}\n"
            # проверяем длину сообщения
            if num_mes > 39:
                # обнуляем длину сообщения
                num_mes = 0
                # добавляем сформированную строку в список для сообщения
                list_text.append(text)
                # обнуляем строку
                text = ''
    # добавляем строки с заказами для последнего сообщения
    list_text.append(text)
    # если список с заказами не пустой
    if list_text:
        # то отправляем сообщения с выполненными заказами
        for text_message in list_text:
            await callback.message.answer(text=f'<b>Отчет о продажах менеджера:</b>\n'
                                               f'{text_message}\n\n',
                                          parse_mode='html')
    else:
        # выводим пустую строку
        await callback.message.answer(text=f'<b>Отчет о продажах менеджера:</b>\n'
                                           f'{text}\n\n',
                                      parse_mode='html')
    # инициализируем переменную для сообщения для итоговых данных
    total_text = ''
    # количество проданных продуктов
    total_order = 0
    # проходим по сформированному словарю и получаем ключ: продукт и значение: количество проданных продуктов
    for key_product, value_product in dict_order_product.items():
        # информация по продукту
        total_text += f'<b>{key_product}:</b> {value_product}\n'
        # общее количество продаж
        total_order += value_product
    await callback.message.answer(text=f'{total_text}'
                                       f'\n'
                                       f'Менеджер выполнил заказов на {count} ₽\n'
                                       f'Количество продаж: {total_order} шт.',
                                  parse_mode='html')

#
#
# # ПРОДАЖИ - для всей компании
# @router.callback_query(F.data == 'salescompany', lambda callback: check_user(callback.message.chat.id))
# async def process_get_stat_select_salescompany(callback: CallbackQuery, state: FSMContext) -> None:
#     logging.info(f'process_get_stat_select_salescompany: {callback.message.chat.id}')
#     user_dict[callback.message.chat.id] = await state.update_data()
#     period = int(user_dict[callback.message.chat.id]['salesperiod'])
#     list_orders = get_list_orders()
#     print(list_orders)
#     count = 0
#     current_date = datetime.now()
#     date1 = current_date.strftime('%m/%d/%y')
#     list_date1 = date1.split('/')
#     date1 = date(int(list_date1[2]), int(list_date1[0]), int(list_date1[1]))
#     text = ''
#     dict_order_product = {}
#     num = 0
#     num_mes = 0
#     list_text = []
#     for order in list_orders[1:]:
#         print(order)
#         list_date2 = order[1].split('/')
#         date2 = date(int(list_date2[2]), int(list_date2[0]), int(list_date2[1]))
#         delta = (date1 - date2).days
#         print(delta)
#         if delta < period:
#             product_list = order[7].split()
#             product = ' '.join(product_list)
#             if not product in dict_order_product.keys():
#                 dict_order_product[product] = 0
#             print(order[5])
#             num += 1
#             num_mes += 1
#             dict_order_product[product] += 1
#             count += int(order[5].split('.')[0])
#             text += f"{num}) Номер заказа: {order[0]} от {order[1]} менеджер {order[3]} стоимость {order[5]}\n"
#             if num_mes > 39:
#                 num_mes = 0
#                 list_text.append(text)
#                 text = ''
#     list_text.append(text)
#     if list_text:
#         for text_message in list_text:
#             await callback.message.answer(text=f'<b>Отчет о продажах компании:</b>\n'
#                                                f'{text_message}\n\n',
#                                           parse_mode='html')
#     else:
#         await callback.message.answer(text=f'<b>Отчет о продаж компании:</b>\n'
#                                            f'{text}\n\n',
#                                       parse_mode='html')
#     total_text = ''
#     total_order = 0
#     for key_product, value_product in dict_order_product.items():
#         total_text += f'<b>{key_product}:</b> {value_product}\n'
#         total_order += value_product
#     await callback.message.answer(text=f'{total_text}'
#                                        f'\n'
#                                        f'Компания выполнила заказов на {count} ₽\n'
#                                        f'Количество продаж: {total_order} шт.',
#                                   parse_mode='html')