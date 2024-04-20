from aiogram.types import CallbackQuery
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext

from keyboards.keyboard_work import keyboards_custom_calendar, keyboards_select_time, keyboards_list_manager_work, \
    keyboards_custom_calendar_block, keyboards_custom_calendar_company
# from services.googlesheets import get_list_workday, set_list_workday
from module.data_base import create_table_workday_leave, get_list_workday, add_manager, set_list_workday,\
    get_list_users, get_user, get_list_workday_all, change_column, update_forward, get_list_workday_all_alert

import logging
from datetime import datetime, timedelta

router = Router()
user_dict = {}


# <editor-fold desc = "СЕКЦИЯ (main keyboard -> [ПЕРСОНАЛ] -> [Смена] - personal_work)">
@router.callback_query(F.data == 'personal_work')
async def process_select_manager_work(callback: CallbackQuery) -> None:
    """
    Выводим клавиатуру (календарь следующего месяца) выбора рабочих смен,
     если смены были выбраны ранее выводим их на клавиатуре
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_select_manager_work: {callback.message.chat.id}')
    # создаем таблицу для списка смен и отпуска
    create_table_workday_leave()
    add_manager(telegram_id=callback.message.chat.id, username=callback.from_user.username)
    list_username = get_list_users()
    await callback.message.edit_reply_markup(text='Для кого требуется получить график смен',
                                             reply_markup=keyboards_list_manager_work(list_manager=list_username))


@router.callback_query(F.data.startswith('workmanager#'))
async def process_select_personal_work(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_select_personal_work: {callback.message.chat.id}')
    # переменная для выбора текущего и будущего месяца (0-будущий месяц, 1-текущий месяц)
    month_work = 1
    # получаем список дат выбранных смен
    # list_workday = get_list_workday(id_telegram=callback.message.chat.id, month_work=month_work)
    telegram_id_work = int(callback.data.split('#')[1])
    list_workday = get_list_workday(telegram_id=telegram_id_work, month_work=month_work)
    if list_workday is None:
        # await callback.message.answer(text='Пользователь не выбирал смен')
        list_workday = [0]
    # получаем текущую дату для вывода календаря
    current_date = datetime.now()
    current_date_string = current_date.strftime('%d/%m/%Y')
    month = int(current_date_string.split('/')[1])
    year = current_date_string.split('/')[2]
    await state.update_data(month_work=month_work)
    await state.update_data(telegram_id_work=telegram_id_work)
    if telegram_id_work == callback.message.chat.id:
        dict_day_busy = await day_is_busy(month_work=month_work)
        # print(dict_day_busy)
        await callback.message.edit_reply_markup(text='Выберите дату смены',
                                                 reply_markup=keyboards_custom_calendar(num_month=month,
                                                                                        num_year=year,
                                                                                        workday=list_workday,
                                                                                        month_work=month_work,
                                                                                        dict_day_busy=dict_day_busy))
    else:
        username = get_user(telegram_id_work)
        await callback.message.edit_reply_markup(text=f'Смены @{username[0]}. Доступен только просмотр',
                                                reply_markup=keyboards_custom_calendar_block(num_month=month,
                                                                                             num_year=year,
                                                                                             workday=list_workday,
                                                                                             month_work=month_work))


@router.callback_query(F.data.startswith('workday_'))
async def process_get_report_change_key(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Выбор даты смены
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_get_report_change_key: {callback.message.chat.id}')
    # обновляем переменные
    user_dict[callback.message.chat.id] = await state.get_data()
    month_work = user_dict[callback.message.chat.id]['month_work']
    current_date = datetime.now()
    current_date_string = current_date.strftime('%d/%m/%Y')
    month = int(current_date_string.split('/')[1])
    year = current_date_string.split('/')[2]
    # выбранная дата
    workday = int(callback.data.split('_')[1])
    # получаем список дат выбранных смен
    # list_workday = get_list_workday(id_telegram=callback.message.chat.id,
    #                                 month_work=month_work)
    list_workday = get_list_workday(telegram_id=callback.message.chat.id,
                                    month_work=month_work)

    if list_workday == ["0"]:
        # print('1')
        # set_list_workday(id_telegram=callback.message.chat.id,
        #                  list_workday=f'{workday}',
        #                  username=callback.from_user.username,
        #                  month_work=month_work)
        set_list_workday(list_workday=f'{workday}',
                         month_work=month_work,
                         telegram_id=callback.message.chat.id)
        list_time = await smena_is_busy(workday=workday, month_work=month_work)
        await callback.message.edit_reply_markup(text='Выберите время смены',
                                                 reply_markup=keyboards_select_time(day=workday,
                                                                                    list_time=list_time))

    else:
        # print('2')
        if f'{workday}/1' in list_workday:
            list_workday.remove(f'{workday}/1')
            # set_list_workday(id_telegram=callback.message.chat.id,
            #                  list_workday=','.join(list_workday),
            #                  username=callback.from_user.username,
            #                  month_work=month_work)
            set_list_workday(list_workday=','.join(list_workday),
                             month_work=month_work,
                             telegram_id=callback.message.chat.id)
            await callback.message.edit_reply_markup(text='Выберите дату смены',
                                                     reply_markup=keyboards_custom_calendar(num_month=month,
                                                                                            num_year=year,
                                                                                            workday=list_workday,
                                                                                            month_work=month_work))
            return
        elif f'{workday}/2' in list_workday:
            list_workday.remove(f'{workday}/2')
            # set_list_workday(id_telegram=callback.message.chat.id,
            #                  list_workday=','.join(list_workday),
            #                  username=callback.from_user.username,
            #                  month_work=month_work)
            set_list_workday(list_workday=','.join(list_workday),
                             month_work=month_work,
                             telegram_id=callback.message.chat.id)
            await callback.message.edit_reply_markup(text='Выберите дату смены',
                                                     reply_markup=keyboards_custom_calendar(num_month=month,
                                                                                            num_year=year,
                                                                                            workday=list_workday,
                                                                                            month_work=month_work))
            return
        else:
            list_workday.append(f'{workday}')
            # set_list_workday(id_telegram=callback.message.chat.id,
            #                  list_workday=','.join(list_workday),
            #                  username=callback.from_user.username,
            #                  month_work=month_work)
            set_list_workday(list_workday=','.join(list_workday),
                             month_work=month_work,
                             telegram_id=callback.message.chat.id)
            list_time = await smena_is_busy(workday=workday, month_work=month_work)
            await callback.message.edit_reply_markup(text='Выберите время смены',
                                                     reply_markup=keyboards_select_time(day=workday,
                                                                                        list_time=list_time))


@router.callback_query(F.data.startswith('time_'))
async def process_get_report_change_key(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Устанавливаем время для выбранной даты
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_get_report_change_key: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    month_work = user_dict[callback.message.chat.id]['month_work']
    current_date = datetime.now()
    current_date_string = current_date.strftime('%d/%m/%Y')
    month = int(current_date_string.split('/')[1])
    year = current_date_string.split('/')[2]
    # list_workday = list(get_list_workday(id_telegram=callback.message.chat.id,
    #                                      month_work=month_work))
    list_workday = get_list_workday(telegram_id=callback.message.chat.id,
                                    month_work=month_work)
    # print(list_workday)
    workday = callback.data.split('_')[2]
    index_ = list_workday.index(workday)
    # если выбрана дневная смена
    if callback.data.split('_')[1] == 'day':
        list_workday[index_] = workday + '/1'
    else:
        list_workday[index_] = workday + '/2'
    # set_list_workday(id_telegram=callback.message.chat.id,
    #                  list_workday=','.join(list_workday),
    #                  username=callback.from_user.username,
    #                  month_work=month_work)
    set_list_workday(list_workday=','.join(list_workday),
                     month_work=month_work,
                     telegram_id=callback.message.chat.id)
    await callback.message.edit_reply_markup(text='Выберите дату смены',
                                             reply_markup=keyboards_custom_calendar(num_month=month,
                                                                                    num_year=year,
                                                                                    workday=list_workday,
                                                                                    month_work=month_work))


@router.callback_query(F.data.startswith('workmonth_'))
async def process_change_month(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_change_month: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    telegram_id_work = user_dict[callback.message.chat.id]['telegram_id_work']
    current_date = datetime.now()
    current_date_string = current_date.strftime('%d/%m/%Y')
    month = int(current_date_string.split('/')[1])
    year = current_date_string.split('/')[2]
    await state.update_data(month_work=int(callback.data.split('_')[1]))
    month_work = int(callback.data.split('_')[1])
    # list_workday = list(get_list_workday(id_telegram=callback.message.chat.id,
    #                                      month_work=month_work))
    list_workday = get_list_workday(telegram_id=telegram_id_work, month_work=month_work)
    if list_workday is None:
        # await callback.message.answer(text='Пользователь не выбирал смен')
        list_workday = [0]
    if telegram_id_work == callback.message.chat.id:
        await callback.message.edit_reply_markup(text='Выберите дату смены',
                                                 reply_markup=keyboards_custom_calendar(num_month=month,
                                                                                        num_year=year,
                                                                                        workday=list_workday,
                                                                                        month_work=month_work))
    else:
        username = get_user(telegram_id_work)
        await callback.message.edit_reply_markup(text=f'Смены @{username[0]}. Доступен только просмотр',
                                                 reply_markup=keyboards_custom_calendar_block(num_month=month,
                                                                                              num_year=year,
                                                                                              workday=list_workday,
                                                                                              month_work=month_work))


async def smena_is_busy(workday: int, month_work: int) -> list:
    workday_all = get_list_workday_all(month_work=month_work)
    # print(workday_all)
    count_1 = 0
    count_2 = 0
    for workday_manager in workday_all:
        # print(workday_manager)
        if workday_manager == '0':
            continue
        list_workdays_manager = workday_manager[0].split(',')
        for day in list_workdays_manager:
            # print(day)
            if '/' in day:
                if int(day.split('/')[0]) == workday:
                    if int(day.split('/')[1]) == 1:
                        count_1 += 1
                    elif int(day.split('/')[1]) == 2:
                        count_2 += 1
    return [count_1, count_2]


async def day_is_busy(month_work: int) -> dict:
    workday_all = get_list_workday_all(month_work=month_work)
    dict_day_busy = {}
    for workday_manager in workday_all:
        if workday_manager == '0':
            continue
        list_workdays_manager = workday_manager[0].split(',')
        for day in list_workdays_manager:
            if '/' in day:
                if day.split('/')[0] not in dict_day_busy.keys():
                    dict_day_busy[day.split('/')[0]] = [0, 0]
                if int(day.split('/')[1]) == 1:
                    dict_day_busy[day.split('/')[0]][0] += 1
                elif int(day.split('/')[1]) == 2:
                    dict_day_busy[day.split('/')[0]][1] += 1
    return dict_day_busy


@router.callback_query(F.data == 'workcompany')
@router.callback_query(F.data.startswith('workmonthcompany_'))
async def process_show_calendar_company(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_show_calendar_company: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    month_work = 1
    if 'workmonthcompany_' in callback.data:
        month_work = int(callback.data.split('_')[1])
    dict_day_busy = await day_is_busy(month_work=month_work)
    # получаем текущую дату для вывода календаря
    current_date = datetime.now()
    current_date_string = current_date.strftime('%d/%m/%Y')
    month = int(current_date_string.split('/')[1])
    year = current_date_string.split('/')[2]
    await callback.message.edit_reply_markup(text='Компания',
                                             reply_markup=keyboards_custom_calendar_company(num_month=month,
                                                                                            num_year=year,
                                                                                            month_work=month_work,
                                                                                            dict_day_busy=dict_day_busy))


@router.callback_query(F.data == 'work_back')
async def process_back_list_manager(callback: CallbackQuery) -> None:
    logging.info(f'process_back_list_manager: {callback.message.chat.id}')
    list_username = get_list_users()
    await callback.message.edit_reply_markup(text='Для кого требуется получить график смен',
                                             reply_markup=keyboards_list_manager_work(list_manager=list_username))
# </editor-fold>


# @router.callback_query(F.data == 'test')
async def scheduler_pass_list_workday():
    change_column()
    update_forward()


@router.callback_query(F.data == 'test')
async def scheduler_alert_20(bot: Bot):
    month_work = 1
    date_today = datetime.now()
    date_tomorrow = date_today + timedelta(days=1)
    date_today_string = date_today.strftime('%d/%m/%Y')
    date_tomorrow_string = date_tomorrow.strftime('%d/%m/%Y')
    if date_today_string.split('/')[1] == date_tomorrow_string.split('/')[1]:
        month_work = 0
    list_workday_all = get_list_workday_all_alert(month_work=month_work)
    tomorrow = date_tomorrow_string.split('/')[0]
    for list_workday_manager in list_workday_all:
        list_workday = list_workday_manager[1].split(',')
        id_manager = list_workday_manager[0]
        if f'{tomorrow}/1' in list_workday:
            await bot.send_message(chat_id=id_manager,
                                   text=f'🔔Напоминаем, что завтра {date_tomorrow_string} с 08:00 до 20:00 у Вас'
                                        f' рабочий день.')


async def scheduler_alert_8(bot: Bot):
    month_work = 0
    date_today = datetime.now()
    date_today_string = date_today.strftime('%d/%m/%Y')
    list_workday_all = get_list_workday_all_alert(month_work=month_work)
    today = date_today_string.split('/')[0]
    for list_workday_manager in list_workday_all:
        list_workday = list_workday_manager[1].split(',')
        id_manager = list_workday_manager[0]
        if f'{today}/2' in list_workday:
            await bot.send_message(chat_id=id_manager,
                                   text=f'🔔Напоминаем, что сегодня {date_today_string} с 20:00 до 00:00 у Вас'
                                        f' рабочая смена.')