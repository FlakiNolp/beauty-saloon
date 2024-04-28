from aiogram.filters.callback_data import CallbackData


class CallbackFabricRemoveSpecialist(CallbackData, prefix='remove_specialist'):
    specialist_id: int
