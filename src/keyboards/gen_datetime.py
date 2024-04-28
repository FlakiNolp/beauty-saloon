import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.abstract_classes.abstract_fabric_method import AbstractFabricMethod
from src.callback_fabrics.switch import CallbackFabricSwitch
from src.database.db_queries.user_queries import UserQueries
from src.callback_fabrics.datetime_fabric import CallbackFabricDatetime
from src.config import NUMBER_OF_INLINE_BUTTONS


class GenDatetime(AbstractFabricMethod):
    def __init__(self):
        self._type = 'datetime'

    @property
    def type(self):
        return self._type

    async def gen_menu(self, session: AsyncSession, service_id: int, beauty_saloon_id: int, specialist_id: int, page: int, **kwargs) -> InlineKeyboardMarkup:
        number_of_datetime = await UserQueries.get_number_of_datetimes(session, service_id, beauty_saloon_id, specialist_id)
        if not number_of_datetime:
            return None
        datetimes = await UserQueries.get_all_datetimes(session, service_id=service_id,
                                                        beauty_saloon_id=beauty_saloon_id, specialist_id=specialist_id,
                                                        limit=NUMBER_OF_INLINE_BUTTONS * 12,
                                                        offset=(page - 1) * NUMBER_OF_INLINE_BUTTONS * 12)
        if not datetimes:
            return None
        kb = [[] for _ in range(13)]
        counter = -1
        for i in range(len(datetimes)):
            if i % NUMBER_OF_INLINE_BUTTONS == 0:
                counter += 1
            kb[counter].append(InlineKeyboardButton(text=f'{datetimes[i].date_time}',
                                                    callback_data=CallbackFabricDatetime(id=datetimes[i].id,
                                                                                         name=str(datetimes[i].date_time).replace(':', '-')).pack()))
        if page > 1:
            kb[12].append(InlineKeyboardButton(text="<", callback_data=CallbackFabricSwitch(direction="<", page=page,
                                                                                            type=self.type).pack()))
        kb[12].append(InlineKeyboardButton(text='Назад', callback_data=CallbackFabricSwitch(direction="back", page=page,
                                                                                            type=self.type).pack()))
        if number_of_datetime / (NUMBER_OF_INLINE_BUTTONS * 12 * page) >= 1:
            kb[12].append(InlineKeyboardButton(text=">", callback_data=CallbackFabricSwitch(direction=">", page=page,
                                                                                            type=self.type).pack()))
        return InlineKeyboardMarkup(inline_keyboard=kb, resize_keyboard=True)
