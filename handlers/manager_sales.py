from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter
from aiogram.types import FSInputFile
import logging

from module.data_base import get_list_users
from datetime import datetime, timedelta
from datetime import date
import requests
import aiogram_calendar
from aiogram.filters.callback_data import CallbackData
import json
from keyboards.keyboard_sales import keyboard_select_period_sales_new, keyboard_select_scale_sales,\
    keyboards_list_product_sales, keyboard_select_scaledetail_sales, keyboard_get_exel
from filter.user_filter import check_user
from filter.admin_filter import chek_admin
from services.googlesheets import get_list_orders
from services.sales_exel import list_sales_to_exel
from module.data_base import get_list_admins
from config_data.config import Config, load_config

router = Router()
config: Config = load_config()


class Sales(StatesGroup):
    period = State()
    period_start = State()
    period_finish = State()


user_dict = {}


def get_telegram_user(user_id, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    # print(response.json())
    return response.json()

# ПРОДАЖИ - период статистики
@router.message(F.text == 'Отчет по продажам')
async def process_get_statistic_sales_period(message: Message) -> None:
    """
    Начало цепочки сообщений для выбора отчета о продажах (выбор периода для которого выдается отчет о продажах)
    Администратор - может выбрать отчет за менеджера или компанию
    Менеджер - может посмотреть отчеты только за менеджеров
    :param message:
    :return:
    """
    logging.info(f'process_get_statistic_sales_period: {message.chat.id}')
    await message.answer(text="Выберите тип отчета",
                         reply_markup=keyboard_select_scaledetail_sales())


@router.callback_query(F.data.startswith('scalesales_'))
async def process_get_scaledetail(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_get_scaledetail: {callback.message.chat.id}')
    await state.update_data(scale_detail=callback.data.split('_')[1])
    await callback.message.answer(text="Выберите период для получения отчета о продажах",
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
@router.callback_query(F.data == 'salesperiod_1')
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
@router.callback_query(F.data == 'salesmanager')
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
@router.callback_query(F.data.startswith('salesmanager#'))
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
    # загрузить из json
    with open('services/dict_sales.json', 'r', encoding='utf-8') as fh:  # открываем файл на чтение
        dict_sales = json.load(fh)  # загружаем из файла данные в словарь data
    # получаем период для которого нужно получить отчет
    if int(user_dict[callback.message.chat.id]['salesperiod']):
        # получаем текущую дату
        current_date = datetime.now()
        # преобразуем ее в строку
        period_start = current_date.strftime('%m/%d/%y')
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        period_finish = tomorrow.strftime('%m/%d/%y')
        # print(period_start, period_finish)
        list_date_start = period_start.split('/')
        date_start = date(int(list_date_start[2]), int(list_date_start[0]), int(list_date_start[1]))
        list_date_finish = period_finish.split('/')
        date_finish = date(int(list_date_finish[2]), int(list_date_finish[0]), int(list_date_finish[1]))
    else:
        period_start = user_dict[callback.message.chat.id]['period_start']
        period_finish = user_dict[callback.message.chat.id]['period_finish']
        # print(period_start, period_finish)
        list_date_start = period_start.split('/')
        date_start = date(int(list_date_start[2]), int(list_date_start[0]), int(list_date_start[1]))
        list_date_finish = period_finish.split('/')
        date_finish = date(int(list_date_finish[2]), int(list_date_finish[0]), int(list_date_finish[1]))
    # получаем весь список заказов
    list_orders = get_list_orders()
    # инициализируем счетчик стоимости выполненных заказов
    count = 0
    # инициализируем переменную для списка заказов
    text = ''
    # инициализируем словарь для суммирования количества по продуктам
    dict_order_product = {}
    # переменная для нумерации заказов
    num = 0
    # переменная ограничивающая длину сообщения
    num_mes = 0
    # список выполненных заказов
    list_text = []
    list_finance_data = []
    list_orders_filter = []
    cost_price = 0
    net_profit = 0
    marginality = 0
    # проходимся по всему списку заказов
    for order in list_orders[1:]:
        # отбираем заказы выполненные выбранным менеджером
        if user_name_manager in order:
            # разбиваем дату выполнения заказа
            list_date_order = order[1].split('/')
            date_order = date(int(list_date_order[2]), int(list_date_order[0]), int(list_date_order[1]))
            # если дата выполнения заказа находится в периоде для предоставления отчета
            if (date_start <= date_order) and (date_order <= date_finish):
                # print(order)
                # убираем пробелы слева и справа у категории
                product_list = order[7].split()
                product = ' '.join(product_list)
                give_ = order[8]
                give = ''
                if give_ == 'online':
                    give = 'Онлайн активация'
                elif give_ == 'phone':
                    give = 'Активация по телефону'
                elif give_ == 'linking':
                    give = 'С привязкой'
                elif give_ == 'hand':
                    give = 'Ручная выдача'
                # если ключа с таким продуктом в словаре еще нет, то создаем его и инициализируем значение ключа 0
                if product in dict_order_product.keys():
                    if give in dict_order_product[product].keys():
                        pass
                    else:
                        dict_order_product[product][give] = 0
                else:
                    dict_order_product[product] = {give: 0}

                # увеличиваем счетчик выполненных заказов
                num += 1
                # увеличиваем счетчик для ограничения длины сообщения
                num_mes += 1
                # увеличиваем счетчик количество проданных продуктов в словаре
                dict_order_product[product][give] += 1
                # print(dict_order_product)
                # увеличиваем сумму выполненных заказов
                count += int(order[5].split('.')[0])
                # формируем строку для вывода в сообщении
                text += f"{num}) Номер заказа: {order[0]} от {order[1]} менеджер {order[3]} стоимость {order[5].split('₽')[0]} ₽\n"
                if date_order >= date(24, 3, 18):
                    # 650.00 ₽/360.00 ₽/44.62/290.00 ₽

                    list_finance_data.append(order[5])
                    cost_price += float(order[5].split('/')[1].split()[0])
                    net_profit += float(order[5].split('/')[3].split()[0])
                    marginality += float(order[5].split('/')[2])
                else:
                    product = order[7].strip()
                    # product = ' '.join()
                    list_finance_data.append(f'{order[5]}/'
                                             f'{dict_sales[product][order[8]][0]}/'
                                             f'{dict_sales[product][order[8]][2]}/'
                                             f'{dict_sales[product][order[8]][3]}')
                    cost_price += float(dict_sales[product][order[8]][0].split()[0])
                    net_profit += float(dict_sales[product][order[8]][3].split()[0])
                    marginality += float(dict_sales[product][order[8]][2])
                # проверяем длину сообщения
                if num_mes > 39:
                    # обнуляем длину сообщения
                    num_mes = 0
                    # добавляем сформированную строку в список для сообщения
                    list_text.append(text)
                    # обнуляем строку
                    text = ''
                list_orders_filter.append(order)
    # добавляем строки с заказами для последнего сообщения
    list_text.append(text)
    scale_detail = user_dict[callback.message.chat.id]['scale_detail']
    if scale_detail == 'details':
        if int(user_dict[callback.message.chat.id]['salesperiod']):
            # если список с заказами не пустой
            if list_text:
                # то отправляем сообщения с выполненными заказами
                for text_message in list_text:
                    await callback.message.answer(text=f'<b>Отчет о продажах менеджера за '
                                                       f'{list_date_start[1]}/{list_date_start[0]}/{list_date_start[2]}'
                                                       f':</b>\n'
                                                       f'{text_message}\n\n',
                                                  parse_mode='html')
            else:
                # выводим пустую строку
                await callback.message.answer(text=f'<b>Отчет о продажах менеджера за '
                                                   f'{list_date_start[1]}/{list_date_start[0]}/{list_date_start[2]}'
                                                   f':</b>\n'
                                                   f'{text}\n\n',
                                              parse_mode='html')
            # if chek_admin(telegram_id=callback.message.chat.id):
            list_sales_to_exel(list_sales=list_orders_filter,
                               date_report=f'{list_date_start[1]}/{list_date_start[0]}/{list_date_start[2]}',
                               count=count,
                               cost_price=cost_price,
                               marginality=round(marginality / len(list_finance_data), 2),
                               net_profit=net_profit,
                               dict_order_product=dict_order_product,
                               admin=chek_admin(telegram_id=callback.message.chat.id))
        else:
            count_days = (date_finish - date_start).days + 1
            # если список с заказами не пустой
            if list_text:
                # то отправляем сообщения с выполненными заказами
                for text_message in list_text:
                    await callback.message.answer(text=f'<b>Отчет о продажах менеджера за {count_days} дня (дней) c'
                                                       f' {list_date_start[1]}/{list_date_start[0]}/'
                                                       f'{list_date_start[2]} по {list_date_finish[1]}/'
                                                       f'{list_date_finish[0]}/{list_date_finish[2]}:</b>\n'
                                                       f'{text_message}\n\n',
                                                  parse_mode='html')
            else:
                # выводим пустую строку
                await callback.message.answer(text=f'<b>Отчет о продажах менеджера за {count_days} дня (дней) c'
                                                   f' {list_date_start[1]}/{list_date_start[0]}/'
                                                   f'{list_date_start[2]} по {list_date_finish[1]}/'
                                                   f'{list_date_finish[0]}/{list_date_finish[2]}:</b>\n'
                                                   f'{text}\n\n',
                                              parse_mode='html')

            list_sales_to_exel(list_sales=list_orders_filter,
                               date_report=f'{list_date_start[1]}/{list_date_start[0]}/'
                                           f'{list_date_start[2]} по {list_date_finish[1]}/{list_date_finish[0]}/'
                                           f'{list_date_finish[2]}',
                               count=count,
                               cost_price=cost_price,
                               marginality=round(marginality / len(list_finance_data), 2),
                               net_profit=net_profit,
                               dict_order_product=dict_order_product,
                               admin=chek_admin(telegram_id=callback.message.chat.id))

    if scale_detail == 'total' or scale_detail == 'details':
        if int(user_dict[callback.message.chat.id]['salesperiod']):
            # инициализируем переменную для сообщения для итоговых данных
            total_text = ''
            # количество проданных продуктов
            total_order = 0
            # проходим по сформированному словарю и получаем ключ: продукт и значение: количество проданных продуктов
            for key_product, value_product in dict_order_product.items():
                total_text += f'<b>{key_product}:</b>\n'
                for key_give, value_give in value_product.items():
                    total_text += f'<i>{key_give}:</i> {value_give}\n'
                    total_order += value_give
                total_text += '--------------\n'
            await callback.message.answer(text=f'<b>Отчет о продажах менеджера за '
                                               f'{list_date_start[1]}/{list_date_start[0]}/{list_date_start[2]}:</b>\n\n'
                                               f'{total_text}\n\n'
                                               f'Менеджер выполнил заказов на {count} ₽\n'
                                               f'Количество продаж: {total_order} шт.',
                                          parse_mode='html')
        else:
            count_days = (date_finish - date_start).days + 1
            # инициализируем переменную для сообщения для итоговых данных
            total_text = ''
            # количество проданных продуктов
            total_order = 0
            # проходим по сформированному словарю и получаем ключ: продукт и значение: количество проданных продуктов
            for key_product, value_product in dict_order_product.items():
                total_text += f'<b>{key_product}:</b>\n'
                for key_give, value_give in value_product.items():
                    total_text += f'<i>{key_give}:</i> {value_give}\n'
                    total_order += value_give
                total_text += '--------------\n'
            await callback.message.answer(text=f'<b>Отчет о продажах менеджера за {count_days} дня (дней) c'
                                               f' {list_date_start[1]}/{list_date_start[0]}/'
                                               f'{list_date_start[2]} по {list_date_finish[1]}/'
                                               f'{list_date_finish[0]}/{list_date_finish[2]}:</b>\n\n'
                                               f'{total_text}\n\n'
                                               f'Менеджер выполнил заказов на {count} ₽\n'
                                               f'Количество продаж: {total_order} шт.',
                                          parse_mode='html')
    if scale_detail == 'details':
        await callback.message.answer(text='Получить отчет в виде файла exel',
                                      reply_markup=keyboard_get_exel())

# ПРОДАЖИ - для всей компании
@router.callback_query(F.data == 'salescompany')
async def process_get_stat_select_salescompany(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_get_stat_select_salescompany: {callback.message.chat.id}')
    # обновляем данные словаря
    user_dict[callback.message.chat.id] = await state.update_data()
    # загрузить из json
    with open('services/dict_sales.json', 'r', encoding='utf-8') as fh:  # открываем файл на чтение
        dict_sales = json.load(fh)  # загружаем из файла данные в словарь data
    # получаем период для которого нужно получить отчет
    if int(user_dict[callback.message.chat.id]['salesperiod']):
        # получаем текущую дату
        current_date = datetime.now()
        # преобразуем ее в строку
        period_start = current_date.strftime('%m/%d/%y')
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        period_finish = tomorrow.strftime('%m/%d/%y')
        # print(period_start, period_finish)
        list_date_start = period_start.split('/')
        date_start = date(int(list_date_start[2]), int(list_date_start[0]), int(list_date_start[1]))
        list_date_finish = period_finish.split('/')
        date_finish = date(int(list_date_finish[2]), int(list_date_finish[0]), int(list_date_finish[1]))
    else:
        period_start = user_dict[callback.message.chat.id]['period_start']
        period_finish = user_dict[callback.message.chat.id]['period_finish']
        # print(period_start, period_finish)
        list_date_start = period_start.split('/')
        date_start = date(int(list_date_start[2]), int(list_date_start[0]), int(list_date_start[1]))
        list_date_finish = period_finish.split('/')
        date_finish = date(int(list_date_finish[2]), int(list_date_finish[0]), int(list_date_finish[1]))
    # получаем весь список заказов
    list_orders = get_list_orders()
    # инициализируем счетчик стоимости выполненных заказов
    count = 0
    # инициализируем переменную для списка заказов
    text = ''
    # инициализируем словарь для суммирования количества по продуктам
    dict_order_product = {}
    # переменная для нумерации заказов
    num = 0
    # переменная ограничивающая длину сообщения
    num_mes = 0
    # список выполненных заказов
    list_text = []
    list_finance_data = []
    list_orders_filter = []
    cost_price = 0
    net_profit = 0
    marginality = 0
    # проходимся по всему списку заказов
    for order in list_orders[1:]:
        # разбиваем дату выполнения заказа
        list_date_order = order[1].split('/')
        date_order = date(int(list_date_order[2]), int(list_date_order[0]), int(list_date_order[1]))
        # если дата выполнения заказа находится в периоде для предоставления отчета
        if (date_start <= date_order) and (date_order <= date_finish):
            # убираем пробелы слева и справа у категории
            product_list = order[7].split()
            product = ' '.join(product_list)
            give_ = order[8]
            give = ''
            if give_ == 'online':
                give = 'Онлайн активация'
            elif give_ == 'phone':
                give = 'Активация по телефону'
            elif give_ == 'linking':
                give = 'С привязкой'
            elif give_ == 'hand':
                give = 'Ручная выдача'
            # если ключа с таким продуктом в словаре еще нет, то создаем его и инициализируем значение ключа 0
            if product in dict_order_product.keys():
                if give in dict_order_product[product].keys():
                    pass
                else:
                    dict_order_product[product][give] = 0
            else:
                dict_order_product[product] = {give: 0}

            # увеличиваем счетчик выполненных заказов
            num += 1
            # увеличиваем счетчик для ограничения длины сообщения
            num_mes += 1
            # увеличиваем счетчик количество проданных продуктов в словаре
            dict_order_product[product][give] += 1
            # увеличиваем сумму выполненных заказов
            count += int(order[5].split('.')[0])
            # формируем строку для вывода в сообщении
            text += f"{num}) Номер заказа: {order[0]} от {order[1]} менеджер {order[3]} стоимость {order[5].split('₽')[0]} ₽\n"
            if date_order >= date(24, 3, 18):
                # 650.00 ₽/360.00 ₽/44.62/290.00 ₽

                list_finance_data.append(order[5])
                cost_price += float(order[5].split('/')[1].split()[0])
                net_profit += float(order[5].split('/')[3].split()[0])
                marginality += float(order[5].split('/')[2])
            else:
                product = order[7].strip()
                # product = ' '.join()
                list_finance_data.append(f'{order[5]}/'
                                         f'{dict_sales[product][order[8]][0]}/'
                                         f'{dict_sales[product][order[8]][2]}/'
                                         f'{dict_sales[product][order[8]][3]}')
                cost_price += float(dict_sales[product][order[8]][0].split()[0])
                net_profit += float(dict_sales[product][order[8]][3].split()[0])
                marginality += float(dict_sales[product][order[8]][2])
            # проверяем длину сообщения
            if num_mes > 39:
                # обнуляем длину сообщения
                num_mes = 0
                # добавляем сформированную строку в список для сообщения
                list_text.append(text)
                # обнуляем строку
                text = ''
            list_orders_filter.append(order)

    # print(list_finance_data)
    # добавляем строки с заказами для последнего сообщения
    list_text.append(text)
    scale_detail = user_dict[callback.message.chat.id]['scale_detail']
    if scale_detail == 'details':
        if int(user_dict[callback.message.chat.id]['salesperiod']):
            # если список с заказами не пустой
            if list_text:
                # то отправляем сообщения с выполненными заказами
                for text_message in list_text:
                    await callback.message.answer(text=f'<b>Отчет о продажах компании за '
                                                       f'{list_date_start[1]}/{list_date_start[0]}/{list_date_start[2]}'
                                                       f':</b>\n'
                                                       f'{text_message}\n\n',
                                                  parse_mode='html')
            else:
                # выводим пустую строку
                await callback.message.answer(text=f'<b>Отчет о продажах компании за {list_date_start[1]}/'
                                                   f'{list_date_start[0]}/{list_date_start[2]}:</b>\n'
                                                   f'{text}\n\n',
                                              parse_mode='html')
            list_sales_to_exel(list_sales=list_orders_filter,
                               date_report=f'{list_date_start[1]}/{list_date_start[0]}/{list_date_start[2]}',
                               count=count,
                               cost_price=cost_price,
                               marginality=round(marginality / len(list_finance_data), 2),
                               net_profit=net_profit,
                               dict_order_product=dict_order_product)
            # file_path = "sales.xlsx"  # или "folder/filename.ext"
            # await callback.message.answer_document(FSInputFile(file_path))
        else:
            count_days = (date_finish - date_start).days + 1
            # если список с заказами не пустой
            if list_text:
                # то отправляем сообщения с выполненными заказами
                for text_message in list_text:
                    await callback.message.answer(text=f'<b>Отчет о продажах компании за {count_days} дня (дней) c'
                                                       f' {list_date_start[1]}/{list_date_start[0]}/'
                                                       f'{list_date_start[2]} по {list_date_finish[1]}/'
                                                       f'{list_date_finish[0]}/{list_date_finish[2]}:</b>\n'
                                                       f'{text_message}\n\n',
                                                  parse_mode='html')
            else:
                # выводим пустую строку
                await callback.message.answer(text=f'<b>Отчет о продажах компании за {count_days} дня (дней) c'
                                                   f' {list_date_start[1]}/{list_date_start[0]}/'
                                                   f'{list_date_start[2]} по {list_date_finish[1]}/'
                                                   f'{list_date_finish[0]}/{list_date_finish[2]}:</b>\n'
                                                   f'{text}\n\n',
                                              parse_mode='html')
            list_sales_to_exel(list_sales=list_orders_filter,
                               date_report=f'{list_date_start[1]}/{list_date_start[0]}/'
                                           f'{list_date_start[2]} по {list_date_finish[1]}/{list_date_finish[0]}/'
                                           f'{list_date_finish[2]}',
                               count=count,
                               cost_price=cost_price,
                               marginality=round(marginality/len(list_finance_data),2),
                               net_profit=net_profit,
                               dict_order_product=dict_order_product)

    if scale_detail == 'total' or scale_detail == 'details':
        if int(user_dict[callback.message.chat.id]['salesperiod']):
            # инициализируем переменную для сообщения для итоговых данных
            total_text = ''
            # количество проданных продуктов
            total_order = 0
            # проходим по сформированному словарю и получаем ключ: продукт и значение: количество проданных продуктов
            for key_product, value_product in dict_order_product.items():
                total_text += f'<b>{key_product}:</b>\n'
                for key_give, value_give in value_product.items():
                    total_text += f'<i>{key_give}:</i> {value_give}\n'
                    total_order += value_give
                total_text += '--------------\n'
            await callback.message.answer(text=f'<b>Отчет о продажах компании за '
                                               f'{list_date_start[1]}/{list_date_start[0]}/{list_date_start[2]}:</b>\n\n'
                                               f'{total_text}\n'
                                               f'Компания выполнила заказов на {count} ₽\n'
                                               f'Себестоимость: {cost_price} ₽\n'
                                               f'Маржинальность: {round(marginality/len(list_finance_data),2)}%\n' 
                                               f'Чистая прибыль: {net_profit} ₽\n'
                                               f'Количество продаж: {total_order} шт.',
                                          parse_mode='html')
        else:
            count_days = (date_finish - date_start).days + 1
            # инициализируем переменную для сообщения для итоговых данных
            total_text = ''
            # количество проданных продуктов
            total_order = 0
            # проходим по сформированному словарю и получаем ключ: продукт и значение: количество проданных продуктов
            for key_product, value_product in dict_order_product.items():
                total_text += f'<b>{key_product}:</b>\n'
                for key_give, value_give in value_product.items():
                    total_text += f'<i>{key_give}:</i> {value_give}\n'
                    total_order += value_give
                total_text += '--------------\n'
            await callback.message.answer(text=f'<b>Отчет о продажах компании за {count_days} дня (дней) c'
                                               f' {list_date_start[1]}/{list_date_start[0]}/'
                                               f'{list_date_start[2]} по {list_date_finish[1]}/'
                                               f'{list_date_finish[0]}/{list_date_finish[2]}:</b>\n\n'
                                               f'{total_text}\n'
                                               f'Компания выполнила заказов на {count} ₽\n'
                                               f'Себестоимость: {cost_price} ₽\n'
                                               f'Маржинальность: {round(marginality/len(list_finance_data),2)}%\n' 
                                               f'Чистая прибыль: {net_profit} ₽\n'
                                               f'Количество продаж: {total_order} шт.',
                                          parse_mode='html')
    if scale_detail == 'details':
        await callback.message.answer(text='Получить отчет в виде файла exel',
                                      reply_markup=keyboard_get_exel())


@router.callback_query(F.data == 'exel')
async def process_get_exel(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_get_exel: {callback.message.chat.id}')
    file_path = "sales.xlsx"  # или "folder/filename.ext"
    await callback.message.answer_document(FSInputFile(file_path))


# ПРОДАЖИ - для выбранного менеджера
async def process_sendler_stat_scheduler(bot: Bot) -> None:
    """
    Рассылка отчета о продажах менеджерам
    """
    logging.info(f'process_sendler_stat_scheduler')
    # обновляем данные словаря

    # получаем текущую дату
    current_date = datetime.now() - timedelta(days=1)
    # преобразуем ее в строку
    period_start = current_date.strftime('%m/%d/%y')
    today = datetime.now()
    tomorrow = today
    period_finish = tomorrow.strftime('%m/%d/%y')
    # print(period_start, period_finish)
    list_date_start = period_start.split('/')
    date_start = date(int(list_date_start[2]), int(list_date_start[0]), int(list_date_start[1]))
    list_date_finish = period_finish.split('/')
    date_finish = date(int(list_date_finish[2]), int(list_date_finish[0]), int(list_date_finish[1]))

    # получаем весь список заказов
    list_orders = get_list_orders()
    # инициализируем счетчик стоимости выполненных заказов
    count = 0

    # инициализируем словарь для суммирования количества по продуктам
    dict_order_product = {}

    # список выполненных заказов
    list_finance_data = []
    list_orders_filter = []
    cost_price = 0
    net_profit = 0
    marginality = 0
    # проходимся по всему списку заказов
    for order in list_orders[1:]:
        # разбиваем дату выполнения заказа
        list_date_order = order[1].split('/')
        date_order = date(int(list_date_order[2]), int(list_date_order[0]), int(list_date_order[1]))
        # если дата выполнения заказа находится в периоде для предоставления отчета
        if (date_start <= date_order) and (date_order <= date_finish):
            # убираем пробелы слева и справа у категории
            product_list = order[7].split()
            product = ' '.join(product_list)
            give_ = order[8]
            give = ''
            if give_ == 'online':
                give = 'Онлайн активация'
            elif give_ == 'phone':
                give = 'Активация по телефону'
            elif give_ == 'linking':
                give = 'С привязкой'
            elif give_ == 'hand':
                give = 'Ручная выдача'
            manager = order[3]
            # если ключа с таким продуктом в словаре еще нет, то создаем его и инициализируем значение ключа 0
            if manager in dict_order_product.keys():
                if product in dict_order_product[manager].keys():
                    if give in dict_order_product[manager][product].keys():
                        pass
                    else:
                        dict_order_product[manager][product][give] = 0
                else:
                    dict_order_product[manager][product] = {give: 0}
            else:
                dict_order_product[manager] = {product: {give: 0}, 'count': 0}

            if 'company' in dict_order_product.keys():
                if product in dict_order_product['company'].keys():
                    if give in dict_order_product['company'][product].keys():
                        pass
                    else:
                        dict_order_product['company'][product][give] = 0
                else:
                    dict_order_product['company'][product] = {give: 0}
            else:
                dict_order_product['company'] = {product: {give: 0}}


            # увеличиваем счетчик количество проданных продуктов в словаре
            dict_order_product[manager][product][give] += 1
            dict_order_product['company'][product][give] += 1
            # увеличиваем сумму выполненных заказов
            count += int(order[5].split('.')[0])
            # формируем строку для вывода в сообщении
            dict_order_product[manager]['count'] += int(order[5].split('.')[0])
            # 650.00 ₽/360.00 ₽/44.62/290.00 ₽
            list_finance_data.append(order[5])
            cost_price += float(order[5].split('/')[1].split()[0])
            net_profit += float(order[5].split('/')[3].split()[0])
            marginality += float(order[5].split('/')[2])

            list_orders_filter.append(order)

    # инициализируем переменную для сообщения для итоговых данных
    total_text = ''
    # количество проданных продуктов
    total_order = 0
    # проходим по сформированному словарю и получаем ключ: продукт и значение: количество проданных продуктов
    for key_product, value_product in dict_order_product['company'].items():
        total_text += f'<b>{key_product}:</b>\n'
        for key_give, value_give in value_product.items():
            total_text += f'<i>{key_give}:</i> {value_give}\n'
            total_order += value_give
        total_text += '--------------\n'
    list_admins = get_list_admins()
    for admin in list_admins:
        result = get_telegram_user(user_id=int(admin[0]), bot_token=config.tg_bot.token)
        if 'result' in result:
            await bot.send_message(chat_id=int(admin[0]),
                                   text=f'<b>Отчет о продажах компании за '
                                        f'{list_date_start[1]}/{list_date_start[0]}/{list_date_start[2]}:</b>\n\n'
                                        f'{total_text}\n'
                                        f'Компания выполнила заказов на {count} ₽\n'
                                        f'Себестоимость: {cost_price} ₽\n'
                                        f'Маржинальность: {round(marginality / len(list_finance_data), 2)}%\n'
                                        f'Чистая прибыль: {net_profit} ₽\n'
                                        f'Количество продаж: {total_order} шт.',
                                   parse_mode='html')
    list_user = get_list_users()
    total_text = ''
    # количество проданных продуктов
    total_order = 0
    for manager in dict_order_product.keys():
        for user in list_user:
            if user[1] == manager:
                for key_product, value_product in dict_order_product[manager].items():
                    total_text += f'<b>{key_product}:</b>\n'
                    for key_give, value_give in value_product.items():
                        total_text += f'<i>{key_give}:</i> {value_give}\n'
                        count += 1
                        total_order += value_give
                    total_text += '--------------\n'
                result = get_telegram_user(user_id=int(user[0]), bot_token=config.tg_bot.token)
                if 'result' in result:
                    await bot.send_message(chat_id=int(user[0]),
                                           text=f'<b>Отчет о продажах менеджера {user[1]} за '
                                                f'{list_date_start[1]}/{list_date_start[0]}/{list_date_start[2]}:</b>\n\n'
                                                f'{total_text}\n'
                                                f'Выполнено заказов на: {dict_order_product[manager]["count"]} ₽\n'
                                                f'Количество продаж: {total_order} шт.',
                                           parse_mode='html')



