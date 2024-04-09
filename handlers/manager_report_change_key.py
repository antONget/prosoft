from aiogram.types import CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter
from aiogram.filters.callback_data import CallbackData
import aiogram_calendar

from keyboards.keyboard_report_change_key import keyboard_select_period_change_key, keyboard_select_scale_change_key, \
    keyboards_list_product_change_key
from filter.admin_filter import check_admin
from filter.user_filter import check_user
from module.data_base import get_list_users
from services.googlesheets import get_list_orders

from datetime import datetime, timedelta
from datetime import date
import logging

router = Router()


class Sales(StatesGroup):
    period = State()
    period_start = State()
    period_finish = State()


user_dict = {}


# <editor-fold desc = "СЕКЦИЯ (main keyboard -> [Отчет] - ОТЧЕТ ЗАМЕНЫ КЛЮЧЕЙ">
@router.callback_query(F.data == 'report_change_key')
async def process_get_report_change_key(callback: CallbackQuery) -> None:
    logging.info(f'process_get_report_change_key: {callback.message.chat.id}')
    await callback.message.answer(text='Функционал "Отчет о заменах ключей" в разработке')
    await callback.message.answer(text="Выберите период для получения отчета о продажах",
                                  reply_markup=keyboard_select_period_change_key())


# календарь
@router.callback_query(F.data == 'changeperiod_calendar')
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
        "Выберите начало периода, для получения отчета о заменах ключей:",
        reply_markup=await calendar.start_calendar(year=int('20' + list_date1[2]), month=int(list_date1[0]))
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
        "Выберите конец периода, для получения отчета о заменах ключей:",
        reply_markup=await calendar.start_calendar(year=int('20' + list_date1[2]), month=int(list_date1[0]))
    )
    await state.set_state(Sales.period_finish)


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(Sales.period_start))
async def process_simple_calendar_start(callback_query: CallbackQuery, callback_data: CallbackData,
                                        state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.edit_text(
            f'Начало периода {date.strftime("%d/%m/%y")}')
        await state.update_data(period_start_change=date.strftime("%m/%d/%y"))
        await process_buttons_press_finish(callback_query, state=state)


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(Sales.period_finish))
async def process_simple_calendar_finish(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback, callback_data)
    if selected:
        await callback.message.edit_text(
            f'Конец периода {date.strftime("%d/%m/%y")}')
        await state.update_data(period_finish_change=date.strftime("%m/%d/%y"))
        await state.update_data(salesperiod_change=0)
        await state.set_state(default_state)
        if check_admin(callback.message.chat.id):
            await callback.message.answer(text='Получить отчет о заменах ключей',
                                          reply_markup=keyboard_select_scale_change_key())
        elif check_user(callback.message.chat.id):
            list_username = get_list_users()
            await callback.message.answer(text='Для кого требуется получить отчет о заменах ключей',
                                          reply_markup=keyboards_list_product_change_key(list_manager=list_username))


# ОТЧЕТ ЗАМЕНЫ КЛЮЧЕЙ - компания или менеджер для админа и менеджер для менеджера
@router.callback_query(F.data == 'changeperiod_1')
async def process_get_changesscale(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Выбор менеджера или компании - для администратора
    Выбор менеджера - для менеджера
    :param callback: salesperiod_{1,7,30}
    :param state:
    :return:
    """
    logging.info(f'process_get_changesscale: {callback.message.chat.id}')
    await state.update_data(salesperiod_change=callback.data.split('_')[1])
    if check_admin(callback.message.chat.id):
        await callback.message.answer(text='Получить отчет о продажах',
                                      reply_markup=keyboard_select_scale_change_key())
    elif check_user(callback.message.chat.id):
        list_username = get_list_users()
        await callback.message.answer(text='Для кого требуется получить отчет о продажах',
                                      reply_markup=keyboards_list_product_change_key(list_manager=list_username))


# ОТЧЕТ ЗАМЕНЫ КЛЮЧЕЙ - менеджер
@router.callback_query(F.data == 'changemanager')
async def process_get_stat_salesmanager(callback: CallbackQuery) -> None:
    """
    Выбор менеджера из списка (клавиатура) для которого требуется получить отчет
    :param callback:
    :return:
    """
    logging.info(f'process_get_stat_salesmanager: {callback.message.chat.id}')
    list_username = get_list_users()
    await callback.message.answer(text='Для кого требуется получить отчет о продажах',
                                  reply_markup=keyboards_list_product_change_key(list_manager=list_username))


# ОТЧЕТ ЗАМЕНЫ КЛЮЧЕЙ - для выбранного менеджера
@router.callback_query(F.data.startswith('changemanager#'))
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
    if int(user_dict[callback.message.chat.id]['salesperiod_change']):
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
        period_start = user_dict[callback.message.chat.id]['period_start_change']
        period_finish = user_dict[callback.message.chat.id]['period_finish_change']
        # print(period_start, period_finish)
        list_date_start = period_start.split('/')
        date_start = date(int(list_date_start[2]), int(list_date_start[0]), int(list_date_start[1]))
        list_date_finish = period_finish.split('/')
        date_finish = date(int(list_date_finish[2]), int(list_date_finish[0]), int(list_date_finish[1]))
    # получаем весь список заказов
    list_orders = get_list_orders()
    # инициализируем счетчик стоимости выполненных заказов
    count = 0
    # проходимся по всему списку заказов
    for order in list_orders[1:]:
        # отбираем заказы выполненные выбранным менеджером
        if user_name_manager in order:
            # разбиваем дату выполнения заказа
            list_date_order = order[1].split('/')
            date_order = date(int(list_date_order[2]), int(list_date_order[0]), int(list_date_order[1]))
            # если дата выполнения заказа находится в периоде для предоставления отчета
            if (date_start <= date_order) and (date_order <= date_finish):
                if order[10] != '':
                    count += 1
    await callback.message.answer(text=f'Количество замен ключей за выбранный период - {count} шт.')


# ОТЧЕТ ЗАМЕНЫ КЛЮЧЕЙ - для всей компании
@router.callback_query(F.data == 'changecompany')
async def process_get_stat_select_salescompany(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_get_stat_select_salescompany: {callback.message.chat.id}')
    # обновляем данные словаря
    user_dict[callback.message.chat.id] = await state.update_data()
    # получаем период для которого нужно получить отчет
    if int(user_dict[callback.message.chat.id]['salesperiod_change']):
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
        period_start = user_dict[callback.message.chat.id]['period_start_change']
        period_finish = user_dict[callback.message.chat.id]['period_finish_change']
        # print(period_start, period_finish)
        list_date_start = period_start.split('/')
        date_start = date(int(list_date_start[2]), int(list_date_start[0]), int(list_date_start[1]))
        list_date_finish = period_finish.split('/')
        date_finish = date(int(list_date_finish[2]), int(list_date_finish[0]), int(list_date_finish[1]))
    # получаем весь список заказов
    list_orders = get_list_orders()
    # инициализируем счетчик стоимости выполненных заказов
    count = 0
    # проходимся по всему списку заказов
    for order in list_orders[1:]:
        # разбиваем дату выполнения заказа
        list_date_order = order[1].split('/')
        date_order = date(int(list_date_order[2]), int(list_date_order[0]), int(list_date_order[1]))
        # если дата выполнения заказа находится в периоде для предоставления отчета
        if (date_start <= date_order) and (date_order <= date_finish):
            if order[10] != '':
                count += 1
    await callback.message.answer(text=f'Количество замен ключей за выбранный период - {count} шт.')
# </editor-fold>
