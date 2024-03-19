from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from module.data_base import create_table_users
import logging
from config_data.config import Config, load_config
from filter.user_filter import check_user
from module.data_base import check_token
from keyboards.keyboards_admin import keyboards_manager

router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()


class User(StatesGroup):
    get_token = State()



user_dict1 = {}


@router.message(CommandStart())
async def process_start_command_user(message: Message, state: FSMContext) -> None:
    """
    Запуск бота пользователем /start
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_start_command_user: {message.chat.id}')
    create_table_users()
    if not check_user(message.chat.id):
        await message.answer(text='Для авторизации в боте пришлите токен который вам отправил администратор')
        await state.set_state(User.get_token)
    else:
        await message.answer(text='Вы авторизованы в боте',
                             reply_markup=keyboards_manager())


# проверяем TOKEN
@router.message(F.text, StateFilter(User.get_token))
async def get_token_user(message: Message, bot: Bot) -> None:
    logging.info(f'get_token_user: {message.chat.id}')
    if check_token(message):
        await message.answer(text='Вы верифицированы',
                             reply_markup=keyboards_manager())
        list_admin = config.tg_bot.admin_ids.split(',')
        # print(list_admin)
        for admin_id in list_admin:
            try:
                await bot.send_message(chat_id=int(admin_id),
                                       text=f'Пользователь @{message.from_user.username} авторизован')
            except:
                pass
    else:
        await message.answer(text='TOKEN не прошел верификацию. Попробуйте с другим TOKEN')