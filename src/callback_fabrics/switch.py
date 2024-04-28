from aiogram.filters.callback_data import CallbackData
from typing import Literal


class CallbackFabricSwitch(CallbackData, prefix='switch'):
    direction: Literal["<", ">", "back"]
    page: int = None
    type: str
