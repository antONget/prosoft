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

from keyboards.keyboards_statistic import keyboard_select_period, keyboard_select_scale, keyboards_list_product
from filter.user_filter import check_user
from filter.admin_filter import chek_admin
from services.googlesheets import get_list_orders


router = Router()
class Stat(StatesGroup):
    period = State()
user_dict = {}

# Статитстика - период статистики
@router.message(F.text == 'Статистика', lambda message: check_user(message.chat.id))
async def process_get_statistic_period(message: Message) -> None:
    logging.info(f'process_get_statistic_period: {message.chat.id}')
    await message.answer(text="Выберите период для получения статистики",
                         reply_markup=keyboard_select_period())


# Статистика - компания или менеджер для админа и менеджер для менеджера
@router.callback_query(F.data.startswith('period'), lambda callback: check_user(callback.message.chat.id))
async def process_get_scale(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_get_scale: {callback.message.chat.id}')
    await state.update_data(period=callback.data.split('_')[1])
    if chek_admin(callback.message.chat.id):
        await callback.message.answer(text='Получить статистику',
                                      reply_markup=keyboard_select_scale())
    elif check_user(callback.message.chat.id):
        list_username = get_list_users()
        await callback.message.answer(text='Для кого требуется получить статистику',
                                      reply_markup=keyboards_list_product(list_manager=list_username))


# Статистика - менеджер
@router.callback_query(F.data == 'manager', lambda callback: check_user(callback.message.chat.id))
async def process_get_stat_manager(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_get_stat_manager: {callback.message.chat.id}')
    list_username = get_list_users()
    await callback.message.answer(text='Для кого требуется получить статистику',
                                  reply_markup=keyboards_list_product(list_manager=list_username))


# Статистика - для выбранного менеджера
@router.callback_query(F.data.startswith('manager_'), lambda callback: check_user(callback.message.chat.id))
async def process_get_stat_select_manager(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_get_stat_select_manager: {callback.message.chat.id}')
    user_name_manager = callback.data.split('_')[1]
    user_dict[callback.message.chat.id] = await state.update_data()
    period = int(user_dict[callback.message.chat.id]['period'])
    list_orders = get_list_orders()
    print(list_orders)
    count = 0
    current_date = datetime.now()
    date1 = current_date.strftime('%m/%d/%y')
    list_date1 = date1.split('/')
    date1 = date(int(list_date1[2]), int(list_date1[0]), int(list_date1[1]))
    for order in list_orders[1:]:
        print(order)
        if user_name_manager in order:
            list_date2 = order[1].split('/')
            date2 = date(int(list_date2[2]), int(list_date2[0]), int(list_date2[1]))
            delta = (date1 - date2).days
            print(delta)
            if delta < period:
                print(order[5])
                count += int(order[5].split('.')[0])
    await callback.message.answer(text=f'Менеджер {user_name_manager} выполнил заказов на {count} ₽')


# Статистика - для выбранного менеджера
@router.callback_query(F.data == 'company', lambda callback: check_user(callback.message.chat.id))
async def process_get_stat_select_company(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_get_stat_select_company: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.update_data()
    period = int(user_dict[callback.message.chat.id]['period'])
    list_orders = get_list_orders()
    print(list_orders)
    count = 0
    current_date = datetime.now()
    date1 = current_date.strftime('%m/%d/%y')
    list_date1 = date1.split('/')
    date1 = date(int(list_date1[2]), int(list_date1[0]), int(list_date1[1]))
    for order in list_orders[1:]:
        print(order)

        list_date2 = order[1].split('/')
        date2 = date(int(list_date2[2]), int(list_date2[0]), int(list_date2[1]))
        delta = (date1 - date2).days
        print(delta)
        if delta < period:
            print(order[5])
            count += int(order[5].split('.')[0])
    await callback.message.answer(text=f'Компания выполнила заказов на {count} ₽')