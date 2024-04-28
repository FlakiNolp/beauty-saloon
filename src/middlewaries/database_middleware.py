from typing import Callable, Dict, Any, Awaitable
from aiogram.types.update import Update
from aiogram import BaseMiddleware

from src.database.database import DataBase

database = DataBase()


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self):
        self.session_factory = DataBase().async_session_maker

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        async with self.session_factory() as session:
            data['session'] = session
            return await handler(event, data)
