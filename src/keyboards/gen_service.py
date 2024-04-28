from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.config import NUMBER_OF_INLINE_BUTTONS
from src.database.db_queries.user_queries import UserQueries
from src.callback_fabrics.service import CallbackFabricService
from src.callback_fabrics.switch import CallbackFabricSwitch
from src.abstract_classes.abstract_fabric_method import AbstractFabricMethod


class GenService(AbstractFabricMethod):
    def __init__(self):
        self._type = 'service'

    @property
    def type(self):
        return self._type

    async def gen_menu(self, session: AsyncSession, page: int = 1, **kwargs) -> InlineKeyboardMarkup:
        number_of_services = await UserQueries.get_number_of_services(session)
        if not number_of_services:
            return None
        services = await UserQueries.get_all_services(session, NUMBER_OF_INLINE_BUTTONS * 12,
                                                      (page - 1) * NUMBER_OF_INLINE_BUTTONS * 12)
        if not services:
            return None
        kb = [[] for _ in range(13)]
        counter = -1
        for i in range(len(services)):
            if i % NUMBER_OF_INLINE_BUTTONS == 0:
                counter += 1
            kb[counter].append(InlineKeyboardButton(text=str(services[i].name),
                                                    callback_data=CallbackFabricService(
                                                        id=services[i].id, name=services[i].name).pack()))
        if page > 1:
            kb[12].append(InlineKeyboardButton(text="<", callback_data=CallbackFabricSwitch(direction="<", page=page,
                                                                                            type=self.type).pack()))
        kb[12].append(InlineKeyboardButton(text='Назад', callback_data=CallbackFabricSwitch(direction="back", page=page,
                                                                                            type=self.type).pack()))
        if number_of_services / (NUMBER_OF_INLINE_BUTTONS * 12 * page) < 0:
            kb[12].append(InlineKeyboardButton(text=">", callback_data=CallbackFabricSwitch(direction=">", page=page,
                                                                                            type=self.type).pack()))
        return InlineKeyboardMarkup(inline_keyboard=kb, resize_keyboard=True)
