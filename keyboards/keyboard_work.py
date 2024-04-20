from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
from datetime import datetime, timedelta


def keyboards_list_manager_work(list_manager: list):
    logging.info("keyboards_list_manager_work")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for i, manager in enumerate(list_manager):
        callback = f'workmanager#{manager[0]}'
        buttons.append(InlineKeyboardButton(
            text=manager[1],
            callback_data=callback))
    button_company = InlineKeyboardButton(
            text='Компания',
            callback_data='workcompany')
    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_company, width=1)
    return kb_builder.as_markup()


def keyboards_custom_calendar(num_month: int, num_year: str, month_work: int, workday: list,
                              dict_day_busy: dict = {}) -> InlineKeyboardMarkup:
    logging.info("keyboards_list_product")
    # список месяцев
    list_month = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    # список дней недели
    list_weekday = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вск']
    # месяц для помещения в клавиатуру
    month = list_month[num_month - 1 + month_work]
    # кнопки для отображения месяца и года
    button_month = InlineKeyboardButton(text=month, callback_data='none')
    button_year = InlineKeyboardButton(text=num_year, callback_data='none')
    button_all = InlineKeyboardButton(text='📆', callback_data=f'all_work_{month_work}')
    # кнопки управления
    if month_work == 1:
        button_pag = InlineKeyboardButton(text='<<<', callback_data='workmonth_0')
    else:
        button_pag = InlineKeyboardButton(text='>>>', callback_data='workmonth_1')
    weekday_ = []
    # клавиатура с днями недели
    for i in list_weekday:
        weekday_.append(InlineKeyboardButton(text=i, callback_data='none'))
    #
    date = datetime(year=int(num_year), month=num_month+month_work, day=1)
    date_2 = datetime(year=int(num_year), month=num_month+1+month_work, day=1)
    first_day = date.weekday()
    count_day = (date_2 - date).days
    day = 0
    flag = 0
    week = []
    for i in range(5):
        if day >= count_day:
            break
        for j in range(7):
            if j == first_day and flag == 0:
                flag = 1
            if flag:
                day += 1
                if f'{day}/1' in workday:
                    week.append(InlineKeyboardButton(text='☀️', callback_data=f'workday_{day}'))
                elif f'{day}/2' in workday:
                    week.append(InlineKeyboardButton(text='🌙', callback_data=f'workday_{day}'))
                elif str(day) in dict_day_busy.keys() and dict_day_busy[f'{day}'][0] == 2 and \
                        dict_day_busy[f'{day}'][1] == 2:
                    week.append(InlineKeyboardButton(text='❌', callback_data=f'none'))
                else:
                    week.append(InlineKeyboardButton(text=str(day), callback_data=f'workday_{day}'))
            else:
                week.append(InlineKeyboardButton(text=' ', callback_data=f'none'))
            if day == count_day:
                flag = 0

    kb_builder = InlineKeyboardBuilder()
    if month_work == 1:
        kb_builder.row(button_pag, button_month, button_year)
    else:
        kb_builder.row(button_month, button_pag, button_year)
    kb_builder.row(*weekday_)
    kb_builder.row(*week, width=7)
    return kb_builder.as_markup()


def keyboards_custom_calendar_block(num_month: int, num_year: str, month_work: int, workday: list):
    logging.info("keyboards_list_product")
    # список месяцев
    list_month = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    # список дней недели
    list_weekday = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вск']
    # месяц для помещения в клавиатуру
    month = list_month[num_month - 1 + month_work]
    # кнопки для отображения месяца и года
    button_month = InlineKeyboardButton(text=month, callback_data='none')
    button_year = InlineKeyboardButton(text=num_year, callback_data='none')
    # кнопки управления
    if month_work == 1:
        button_pag = InlineKeyboardButton(text='<<<', callback_data='workmonth_0')
    else:
        button_pag = InlineKeyboardButton(text='>>>', callback_data='workmonth_1')
    weekday_ = []
    # клавиатура с днями недели
    for i in list_weekday:
        weekday_.append(InlineKeyboardButton(text=i, callback_data='none'))
    #
    date = datetime(year=int(num_year), month=num_month+month_work, day=1)
    date_2 = datetime(year=int(num_year), month=num_month+1+month_work, day=1)
    first_day = date.weekday()
    count_day = (date_2 - date).days
    day = 0
    flag = 0
    week = []
    for i in range(5):
        if day >= count_day:
            break
        for j in range(7):
            if j == first_day and flag == 0:
                flag = 1
            if flag:
                day += 1
                if f'{day}/1' in workday:
                    week.append(InlineKeyboardButton(text='☀️', callback_data=f'none'))
                elif f'{day}/2' in workday:
                    week.append(InlineKeyboardButton(text='🌙', callback_data=f'none'))
                else:
                    week.append(InlineKeyboardButton(text=str(day), callback_data=f'none'))
            else:
                week.append(InlineKeyboardButton(text=' ', callback_data=f'none'))
            if day == count_day:
                flag = 0

    kb_builder = InlineKeyboardBuilder()
    if month_work == 1:
        kb_builder.row(button_pag, button_month, button_year)
    else:
        kb_builder.row(button_month, button_pag, button_year)
    kb_builder.row(*weekday_)
    kb_builder.row(*week, width=7)
    return kb_builder.as_markup()


def keyboards_custom_calendar_company(num_month: int, num_year: str, month_work: int,
                                        dict_day_busy: dict = {}) -> InlineKeyboardMarkup:
    logging.info("keyboards_list_product")
    # список месяцев
    list_month = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    # список дней недели
    list_weekday = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вск']
    # месяц для помещения в клавиатуру
    month = list_month[num_month - 1 + month_work]
    # кнопки для отображения месяца и года
    button_month = InlineKeyboardButton(text=month, callback_data='none')
    button_year = InlineKeyboardButton(text=num_year, callback_data='none')
    button_all = InlineKeyboardButton(text='📆', callback_data=f'all_work_{month_work}')
    # кнопки управления
    if month_work == 1:
        button_pag = InlineKeyboardButton(text='<<<', callback_data='workmonthcompany_0')
    else:
        button_pag = InlineKeyboardButton(text='>>>', callback_data='workmonthcompany_1')
    weekday_ = []
    # клавиатура с днями недели
    for i in list_weekday:
        weekday_.append(InlineKeyboardButton(text=i, callback_data='none'))
    #
    date = datetime(year=int(num_year), month=num_month+month_work, day=1)
    date_2 = datetime(year=int(num_year), month=num_month+1+month_work, day=1)
    first_day = date.weekday()
    count_day = (date_2 - date).days
    day = 0
    flag = 0
    week = []
    for i in range(5):
        if day >= count_day:
            break
        for j in range(7):
            if j == first_day and flag == 0:
                flag = 1
            if flag:
                day += 1
                # если заняты все дневные смены, а вечерних недостаточно
                if str(day) in dict_day_busy.keys() and\
                        dict_day_busy[f'{day}'][0] == 2 and dict_day_busy[f'{day}'][1] == 0:
                    week.append(InlineKeyboardButton(text='🌙', callback_data=f'none'))
                # если заняты все ночные смены, а дневных недостаточно
                elif str(day) in dict_day_busy.keys() and \
                        dict_day_busy[f'{day}'][0] == 0 and dict_day_busy[f'{day}'][1] == 2:
                    week.append(InlineKeyboardButton(text='☀️', callback_data=f'none'))
                # если заняты все дневные смены, а вечерних недостаточно
                elif str(day) in dict_day_busy.keys() and \
                     dict_day_busy[f'{day}'][0] < 2 and dict_day_busy[f'{day}'][1] < 2:
                    week.append(InlineKeyboardButton(text='⚠️', callback_data=f'none'))
                elif str(day) in dict_day_busy.keys() and dict_day_busy[f'{day}'][0] == 2 and \
                        dict_day_busy[f'{day}'][1] == 2:
                    week.append(InlineKeyboardButton(text='✅', callback_data=f'none'))
                else:
                    week.append(InlineKeyboardButton(text=str(day), callback_data=f'none'))
            else:
                week.append(InlineKeyboardButton(text=' ', callback_data=f'none'))
            if day == count_day:
                flag = 0
    kb_builder = InlineKeyboardBuilder()
    if month_work == 1:
        kb_builder.row(button_pag, button_month, button_year)
    else:
        kb_builder.row(button_month, button_pag, button_year)
    kb_builder.row(*weekday_)
    kb_builder.row(*week, width=7)
    return kb_builder.as_markup()

def keyboards_select_time(day: int, list_time: list) -> InlineKeyboardMarkup:
    logging.info("keyboards_cancel_append_key")
    if list_time[0] >= 2:
        button_1 = InlineKeyboardButton(text='❌ 08 - 20', callback_data=f'none')
    else:
        button_1 = InlineKeyboardButton(text='08 - 20', callback_data=f'time_day_{day}')
    if list_time[1] >= 2:
        button_2 = InlineKeyboardButton(text='❌ 20 - 00', callback_data=f'none')
    else:
        button_2 = InlineKeyboardButton(text='20 - 00', callback_data=f'time_night_{day}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]], )
    return keyboard