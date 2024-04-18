from aiogram.types import CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from keyboards.keyboard_work import keyboards_custom_calendar, keyboards_select_time
from services.googlesheets import get_list_workday, set_list_workday

import logging
from datetime import datetime

router = Router()
user_dict = {}


@router.callback_query(F.data == 'personal_work')
async def process_get_report_change_key(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Выводим клавиатуру выбора рабочих смен, если смены были выбраны ранее выводим их на клавиатуре
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_get_report_change_key: {callback.message.chat.id}')
    month_work = 0
    # получаем список дат выбранных смен
    list_workday = get_list_workday(id_telegram=callback.message.chat.id, month_work=month_work)
    # получаем текущую дату для вывода календаря
    current_date = datetime.now()
    current_date_string = current_date.strftime('%d/%m/%Y')
    month = int(current_date_string.split('/')[1])
    year = current_date_string.split('/')[2]
    await state.update_data(month_work=month_work)
    await callback.message.answer(text='Выберите дату смены',
                                  reply_markup=keyboards_custom_calendar(num_month=month,
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
    user_dict[callback.message.chat.id] = await state.get_data()
    month_work = user_dict[callback.message.chat.id]['month_work']
    current_date = datetime.now()
    current_date_string = current_date.strftime('%d/%m/%Y')
    month = int(current_date_string.split('/')[1])
    year = current_date_string.split('/')[2]
    # выбранная дата
    workday = int(callback.data.split('_')[1])
    # получаем список дат выбранных смен
    list_workday = get_list_workday(id_telegram=callback.message.chat.id,
                                    month_work=month_work)
    if list_workday == [0]:
        set_list_workday(id_telegram=callback.message.chat.id,
                         list_workday=f'{workday}',
                         username=callback.from_user.username,
                         month_work=month_work)
    else:
        if f'{workday}/1' in list_workday:
            list_workday.remove(f'{workday}/1')
            set_list_workday(id_telegram=callback.message.chat.id,
                             list_workday=','.join(list_workday),
                             username=callback.from_user.username,
                             month_work=month_work)
            await callback.message.edit_reply_markup(text='Выберите дату смены',
                                                     reply_markup=keyboards_custom_calendar(num_month=month,
                                                                                            num_year=year,
                                                                                            workday=list_workday,
                                                                                            month_work=month_work))
            return
        elif f'{workday}/2' in list_workday:
            list_workday.remove(f'{workday}/2')
            set_list_workday(id_telegram=callback.message.chat.id,
                             list_workday=','.join(list_workday),
                             username=callback.from_user.username,
                             month_work=month_work)
            await callback.message.edit_reply_markup(text='Выберите дату смены',
                                                     reply_markup=keyboards_custom_calendar(num_month=month,
                                                                                            num_year=year,
                                                                                            workday=list_workday,
                                                                                            month_work=month_work))
            return
        else:
            list_workday.append(f'{workday}')
        set_list_workday(id_telegram=callback.message.chat.id,
                         list_workday=','.join(list_workday),
                         username=callback.from_user.username,
                         month_work=month_work)
    await callback.message.edit_reply_markup(text='Выберите время смены',
                                             reply_markup=keyboards_select_time(workday))


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
    list_workday = list(get_list_workday(id_telegram=callback.message.chat.id,
                                         month_work=month_work))
    # print(list_workday)
    workday = callback.data.split('_')[2]
    index_ = list_workday.index(workday)
    # если выбрана дневная смена
    if callback.data.split('_')[1] == 'day':
        list_workday[index_] = workday + '/1'
    else:
        list_workday[index_] = workday + '/2'
    set_list_workday(id_telegram=callback.message.chat.id,
                     list_workday=','.join(list_workday),
                     username=callback.from_user.username,
                     month_work=month_work)
    await callback.message.edit_reply_markup(text='Выберите дату смены',
                                             reply_markup=keyboards_custom_calendar(num_month=month,
                                                                                    num_year=year,
                                                                                    workday=list_workday,
                                                                                    month_work=month_work))


@router.callback_query(F.data.startswith('workmonth_'))
async def process_change_month(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_change_month: {callback.message.chat.id}')
    current_date = datetime.now()
    current_date_string = current_date.strftime('%d/%m/%Y')
    month = int(current_date_string.split('/')[1])
    year = current_date_string.split('/')[2]
    await state.update_data(month_work=int(callback.data.split('_')[1]))
    month_work = int(callback.data.split('_')[1])
    list_workday = list(get_list_workday(id_telegram=callback.message.chat.id,
                                         month_work=month_work))
    await callback.message.edit_reply_markup(text='Выберите дату смены',
                                             reply_markup=keyboards_custom_calendar(num_month=month,
                                                                                    num_year=year,
                                                                                    workday=list_workday,
                                                                                    month_work=month_work))