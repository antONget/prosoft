import logging
from typing import Any, Awaitable, Callable, Dict
from filter.user_filter import check_user
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)


class Middleware_message(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        if not check_user(event.chat.id):
            return
        result = await handler(event, data)
        return result


class Middleware_callback(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        if not check_user(event.message.chat.id):
            return
        result = await handler(event, data)
        return result