from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
from datetime import datetime, timedelta


def keyboards_custom_calendar(num_month: int, num_year: str, month_work: int, workday: list = [0]):
    logging.info("keyboards_list_product")

    list_month = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    list_weekday = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вск']

    month = list_month[num_month - month_work]
    button_month = InlineKeyboardButton(text=month, callback_data='none')
    button_year = InlineKeyboardButton(text=num_year, callback_data='none')
    if month_work == 0:
        button_pag = InlineKeyboardButton(text='<<<', callback_data='workmonth_1')
    else:
        button_pag = InlineKeyboardButton(text='>>>', callback_data='workmonth_0')
    weekday = []
    for i in list_weekday:
        weekday.append(InlineKeyboardButton(text=i, callback_data='none'))

    date = datetime(year=int(num_year), month=num_month, day=1)
    date_2 = datetime(year=int(num_year), month=num_month+1, day=1)
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
                else:
                    week.append(InlineKeyboardButton(text=str(day), callback_data=f'workday_{day}'))
            else:
                week.append(InlineKeyboardButton(text=' ', callback_data=f'none'))
            if day == count_day:
                flag = 0

    kb_builder = InlineKeyboardBuilder()
    if month_work == 0:
        kb_builder.row(button_pag, button_month, button_year)
    else:
        kb_builder.row(button_month, button_pag, button_year)
    kb_builder.row(*weekday)
    kb_builder.row(*week, width=7)
    return kb_builder.as_markup()


def keyboards_select_time(day):
    logging.info("keyboards_cancel_append_key")
    button_1 = InlineKeyboardButton(text='08 - 20', callback_data=f'time_day_{day}')
    button_2 = InlineKeyboardButton(text='20 - 00', callback_data=f'time_night_{day}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]], )
    return keyboard