from aiogram.types import CallbackQuery
from aiogram import F, Router

import logging

router = Router()


@router.callback_query(F.data == 'report_change_key')
async def process_get_report_change_key(callback: CallbackQuery) -> None:
    logging.info(f'process_get_report_change_key: {callback.message.chat.id}')
    await callback.message.answer(text='Функционал "Отчет о заменах ключей" в разработке')
