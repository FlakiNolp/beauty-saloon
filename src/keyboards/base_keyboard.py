from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.abstract_classes.abstract_fabric_method import AbstractFabricMethod
from src.callback_fabrics.switch import CallbackFabricSwitch
from src.database.db_queries.user_queries import UserQueries
from src.callback_fabrics.beauty_saloon import CallbackFabricBeautySaloon
from src.config import NUMBER_OF_INLINE_BUTTONS


class BaseKeyboard(AbstractFabricMethod):
    def __init__(self, type_keyboard: str):
        self._type = type_keyboard

    @property
    def type(self):
        return self._type

    async def gen_menu(self, session: AsyncSession, service_id: int, page: int, **kwargs) -> InlineKeyboardMarkup:
        number_of_beauty_saloons = await UserQueries.get_number_of_saloons_by_service(session, service_id)
        if not number_of_beauty_saloons:
            return None
        beauty_saloons = await UserQueries.get_all_beauty_saloons_by_service(session, service_id,
                                                                             NUMBER_OF_INLINE_BUTTONS * 12,
                                                                             (page - 1) * NUMBER_OF_INLINE_BUTTONS * 12)
        if not beauty_saloons:
            return None
        kb = [[] for _ in range(13)]
        counter = -1
        for i in range(len(beauty_saloons)):
            if i % NUMBER_OF_INLINE_BUTTONS == 0:
                counter += 1
            kb[counter].append(InlineKeyboardButton(text=str(beauty_saloons[i].name),
                                                    callback_data=CallbackFabricBeautySaloon(id=beauty_saloons[i].id,
                                                                                         name=beauty_saloons[i].name).pack()))
        if page > 1:
            kb[12].append(InlineKeyboardButton(text="<", callback_data=CallbackFabricSwitch(direction="<", page=page,
                                                                                           type=self.type).pack()))
        kb[12].append(InlineKeyboardButton(text='Назад', callback_data=CallbackFabricSwitch(direction="back", page=page, type=self.type).pack()))
        if number_of_beauty_saloons / (NUMBER_OF_INLINE_BUTTONS * 12 * page) < 0:
            kb[12].append(InlineKeyboardButton(text=">", callback_data=CallbackFabricSwitch(direction=">", page=page,
                                                                                           type=self.type).pack()))
        return InlineKeyboardMarkup(inline_keyboard=kb, resize_keyboard=True)