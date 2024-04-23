from aiogram.types import CallbackQuery
from aiogram import F, Router, Bot
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter
import aiogram_calendar
from keyboards.keyboard_leave import keyboard_send_admin, keyboard_confirm_admin_leave, keyboard_send_change_leave, \
    keyboard_send_change_leave_confirm
from module.data_base import get_list_admins, update_leave, get_user
from config_data.config import Config, load_config

from datetime import datetime
import logging
import requests

router = Router()
config: Config = load_config()
user_dict = {}


class Leave(StatesGroup):
    period = State()
    period_start = State()
    period_finish = State()
    period_start1 = State()
    period_finish1 = State()


def get_telegram_user(user_id, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    return response.json()


@router.callback_query(F.data == 'personal_leave')
async def process_personal_leave(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_personal_leave: {callback.message.chat.id}')
    # await callback.message.answer(text='Функционал "Согласование отпуска менеджера" в разработке')
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2024, 1, 1), datetime(2028, 12, 31))
    # получаем текущую дату
    current_date = datetime.now()
    # преобразуем ее в строку
    date1 = current_date.strftime('%m/%d/%y')
    # преобразуем дату в список
    list_date1 = date1.split('/')
    await callback.message.answer(
        "Выберите дату начала отпуска:                         .",
        reply_markup=await calendar.start_calendar(year=int('20'+list_date1[2]), month=int(list_date1[0]))
    )
    await state.set_state(Leave.period_start)


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
        "Выберите дату окончания отпуска:                         .",
        reply_markup=await calendar.start_calendar(year=int('20'+list_date1[2]), month=int(list_date1[0]))
    )
    await state.set_state(Leave.period_finish)


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(Leave.period_start))
async def process_simple_calendar_start(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.edit_text(
            f'Дата начала отпуска {date.strftime("%d/%m/%y")}')
        await state.update_data(period_start=date.strftime("%d/%m/%y"))
        await process_buttons_press_finish(callback_query, state=state)


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(Leave.period_finish))
async def process_simple_calendar_finish(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    logging.info("process_simple_calendar_finish")
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback, callback_data)
    if selected:
        await state.set_state(default_state)
        await callback.message.edit_text(
            f'Дата окончания отпуска {date.strftime("%d/%m/%y")}')
        await state.update_data(period_finish=date.strftime("%d/%m/%y"))
        user_dict[callback.message.chat.id] = await state.update_data()

        await callback.message.answer(text=f'Отправить на согласование даты отпуска:\n'
                                           f'{user_dict[callback.message.chat.id]["period_start"]}-'
                                           f'{user_dict[callback.message.chat.id]["period_finish"]}',
                                      reply_markup=keyboard_send_admin())


@router.callback_query(F.data == 'sendadmin')
async def process_confirm_leave(callback: CallbackQuery, bot: Bot, state: FSMContext):
    logging.info("process_confirm_leave")
    await callback.message.edit_reply_markup(text='Даты отправлены на согласование')
    await callback.message.answer(text='Даты отправлены на согласование')
    list_admin = get_list_admins()
    for id_admin in list_admin:
        result = get_telegram_user(user_id=id_admin[0], bot_token=config.tg_bot.token)
        if 'result' in result:
            user_dict[callback.message.chat.id] = await state.update_data()
            await bot.send_message(chat_id=id_admin[0],
                                   text=f'Менеджер {callback.from_user.username} просит согласовать отпуск на период с '
                                        f'{user_dict[callback.message.chat.id]["period_start"]} по '
                                        f'{user_dict[callback.message.chat.id]["period_finish"]}',
                                   reply_markup=keyboard_confirm_admin_leave(callback.message.chat.id))


@router.callback_query(F.data.startswith('adminleave'))
async def process_confirm_leave(callback: CallbackQuery, bot: Bot, state: FSMContext):
    logging.info("process_confirm_leave")
    answer_admin = callback.data.split('_')[1]
    id_manager = int(callback.data.split("_")[2])
    user_dict[callback.message.chat.id] = await state.update_data()
    if answer_admin == 'confirm':
        await bot.send_message(chat_id=id_manager,
                               text=f'Ваш отпуск согласован')
        leave_manager = f'{user_dict[id_manager]["period_start"]}-{user_dict[id_manager]["period_finish"]}'
        update_leave(leave=leave_manager, telegram_id=id_manager)
    elif answer_admin == 'cancel':
        await bot.send_message(chat_id=id_manager,
                               text=f'Ваш отпуск отклонен')
    elif answer_admin == 'other':
        await bot.send_message(chat_id=id_manager,
                               text=f'Предложены другие сроки')
        await state.update_data(admin_cange_leave=f'{id_manager}')
        await process_personal_leave_admin(callback=callback, state=state)


async def process_personal_leave_admin(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_personal_leave: {callback.message.chat.id}')
    # await callback.message.answer(text='Функционал "Согласование отпуска менеджера" в разработке')
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2024, 1, 1), datetime(2028, 12, 31))
    # получаем текущую дату
    current_date = datetime.now()
    # преобразуем ее в строку
    date1 = current_date.strftime('%m/%d/%y')
    # преобразуем дату в список
    list_date1 = date1.split('/')
    user_dict[callback.message.chat.id] = await state.get_data()
    id_manager = int(user_dict[callback.message.chat.id]["admin_cange_leave"])
    print(id_manager)
    manager_username = get_user(id_manager)[0]
    await callback.message.answer(
        text=f"Выберите дату начала отпуска для @{manager_username}",
        reply_markup=await calendar.start_calendar(year=int('20' + list_date1[2]), month=int(list_date1[0]))
    )
    await state.set_state(Leave.period_start1)


async def process_buttons_press_finish_admin(callback: CallbackQuery, state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2024, 1, 1), datetime(2028, 12, 31))
    # получаем текущую дату
    current_date = datetime.now()
    # преобразуем ее в строку
    date1 = current_date.strftime('%m/%d/%y')
    # преобразуем дату в список
    list_date1 = date1.split('/')
    user_dict[callback.message.chat.id] = await state.get_data()
    id_manager = int(user_dict[callback.message.chat.id]["admin_cange_leave"])
    manager_username = get_user(id_manager)[0]
    await callback.message.answer(
        text=f"Выберите дату начала отпуска для @{manager_username}",
        reply_markup=await calendar.start_calendar(year=int('20' + list_date1[2]), month=int(list_date1[0]))
    )
    await state.set_state(Leave.period_finish1)


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(Leave.period_start1))
async def process_simple_calendar_start(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.edit_text(
            f'Дата начала отпуска {date.strftime("%d/%m/%y")}')
        await state.update_data(period_start=date.strftime("%d/%m/%y"))
        await process_buttons_press_finish_admin(callback_query, state=state)


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(Leave.period_finish1))
async def process_simple_calendar_finish(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    logging.info("process_simple_calendar_finish")
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback, callback_data)
    if selected:
        await state.set_state(default_state)
        await callback.message.edit_text(
            f'Дата окончания отпуска {date.strftime("%d/%m/%y")}')
        await state.update_data(period_finish=date.strftime("%d/%m/%y"))
        user_dict[callback.message.chat.id] = await state.update_data()
        id_manager = int(user_dict[callback.message.chat.id]["admin_cange_leave"])
        manager_username = get_user(id_manager)[0]
        change_leave = f'{user_dict[callback.message.chat.id]["period_start"]}-{user_dict[callback.message.chat.id]["period_finish"]}'
        await callback.message.answer(text=f'Отправить на согласование даты отпуска менеджеру @{manager_username}:\n',
                                      reply_markup=keyboard_send_change_leave(id_manager, change_leave,
                                                                              id_admin=callback.message.chat.id))


@router.callback_query(F.data.startswith('sendchangeleave_'))
async def process_confirm_leave_change(callback: CallbackQuery, bot: Bot, state: FSMContext):
    logging.info("process_confirm_leave_change")
    id_manager = callback.data.split('_')[1]
    leave_change = callback.data.split('_')[2]
    admin_username = get_user(int(callback.data.split('_')[3]))[0]
    await bot.send_message(chat_id=id_manager,
                           text=f'Админ @{admin_username} предложил следующий период для отпуска:\n'
                                f'{leave_change}',
                           reply_markup=keyboard_send_change_leave_confirm(id_manager=id_manager,
                                                                           change_leave=leave_change,
                                                                           id_admin=int(callback.data.split('_')[3])))


@router.callback_query(F.data.startswith('sendchangeleaveconfirm_'))
async def process_confirm_leave_change(callback: CallbackQuery, bot: Bot):
    logging.info("process_confirm_leave_change")
    leave_manager = callback.data.split('_')[2]
    id_manager = int(callback.data.split('_')[1])
    username_manager = get_user(id_manager)[0]
    id_admin = int(callback.data.split('_')[3])
    update_leave(leave=leave_manager, telegram_id=id_manager)
    await bot.send_message(chat_id=id_admin,
                           text=f'Менеджер @{username_manager} согласился на предложенный отпуск в период с {leave_manager}')
    await callback.message.edit_reply_markup(text='')
    await callback.message.answer(text='Ваш отпуск записан в базу')
