from aiogram import Router
from aiogram.types import Message, CallbackQuery

import logging

router = Router()


@router.callback_query()
async def all_calback(callback: CallbackQuery) -> None:
    logging.info(f'all_calback: {callback.message.chat.id}')
    # print(callback.data)


@router.message()
async def all_message(message: Message) -> None:
    logging.info(f'all_message')
    if message.photo:
        logging.info(f'all_message message.photo')
        # print(message.photo[-1].file_id)

    if message.sticker:
        logging.info(f'all_message message.sticker')
        # Получим ID Стикера
        # print(message.sticker.file_id)
