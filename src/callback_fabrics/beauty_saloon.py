from src.callback_fabrics.base_callback_fabric import BaseCallbackFabric
from aiogram.filters.callback_data import CallbackData


class CallbackFabricBeautySaloon(BaseCallbackFabric, CallbackData, prefix='beauty_saloon'):
    ...