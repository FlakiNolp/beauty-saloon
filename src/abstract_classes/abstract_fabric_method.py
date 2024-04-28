from abc import ABC, abstractmethod
from aiogram.types import InlineKeyboardMarkup

from sqlalchemy.ext.asyncio import AsyncSession


class AbstractFabricMethod(ABC):
    @property
    @abstractmethod
    def type(self):
        return self.type

    @abstractmethod
    async def gen_menu(self, **kwargs) -> InlineKeyboardMarkup:
        raise NotImplementedError
