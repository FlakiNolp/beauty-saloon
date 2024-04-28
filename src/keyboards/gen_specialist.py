from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.abstract_classes.abstract_fabric_method import AbstractFabricMethod
from src.callback_fabrics.switch import CallbackFabricSwitch
from src.config import NUMBER_OF_INLINE_BUTTONS
from src.database.db_queries.user_queries import UserQueries
from src.callback_fabrics.specialist import CallbackFabricSpecialist


class GenSpecialist(AbstractFabricMethod):
    def __init__(self):
        self._type = 'specialist'

    @property
    def type(self):
        return self._type

    async def gen_menu(self, session: AsyncSession, service_id: int, beauty_saloon_id: int, page: int, **kwargs) -> InlineKeyboardMarkup:
        number_of_specialist = await UserQueries.get_number_of_specialist(session, service_id, beauty_saloon_id)
        if not number_of_specialist:
            return None
        specialists = await UserQueries.get_all_specialists(session, service_id, beauty_saloon_id, NUMBER_OF_INLINE_BUTTONS * 2, (page - 1) * NUMBER_OF_INLINE_BUTTONS * 2)
        if not specialists:
            return None
        kb = [[] for _ in range(13)]
        counter = -1
        for i in range(len(specialists)):
            if i % NUMBER_OF_INLINE_BUTTONS == 0:
                counter += 1
            kb[counter].append(InlineKeyboardButton(text=f'{specialists[i][0].last_name} {specialists[i][0].first_name} {str(specialists[i][1])} Опыт: {str(specialists[i][0].experience)} год(а)',
                                                    callback_data=CallbackFabricSpecialist(id=specialists[i][0].id,
                                                                                           name=f'{specialists[i][0].last_name} {specialists[i][0].first_name} {str(specialists[i][1])}').pack()))
        if page > 1:
            kb[12].append(InlineKeyboardButton(text="<", callback_data=CallbackFabricSwitch(direction="<", page=page,
                                                                                            type=self.type).pack()))
        kb[12].append(InlineKeyboardButton(text='Назад', callback_data=CallbackFabricSwitch(direction="back", page=page,
                                                                                            type=self.type).pack()))
        if number_of_specialist / (NUMBER_OF_INLINE_BUTTONS * 12 * page) < 0:
            kb[12].append(InlineKeyboardButton(text=">", callback_data=CallbackFabricSwitch(direction=">", page=page,
                                                                                            type=self.type).pack()))
        return InlineKeyboardMarkup(inline_keyboard=kb, resize_keyboard=True)
