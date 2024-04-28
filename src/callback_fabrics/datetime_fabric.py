from src.callback_fabrics.base_callback_fabric import BaseCallbackFabric
from aiogram.filters.callback_data import CallbackData


class CallbackFabricDatetime(BaseCallbackFabric, CallbackData, prefix='datetime'):
    ...