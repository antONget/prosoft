from aiogram.types import CallbackQuery
from aiogram import F, Router

import logging

router = Router()


@router.callback_query(F.data == 'personal_work')
async def process_get_report_change_key(callback: CallbackQuery) -> None:
    logging.info(f'process_get_report_change_key: {callback.message.chat.id}')
    await callback.message.answer(text='Функционал "Выбор рабочих смен" в разработке')
