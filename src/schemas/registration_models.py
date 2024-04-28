import datetime
from pydantic import BaseModel, Field
from typing import Literal

from src.aiogram_calendar.dialog_calendar import DialogCalendar


class RegistrationType(BaseModel):
    user_type: Literal['user', 'saloon']


class RegistrationNames(BaseModel):
    first_name: str = Field(ge=2, le=25, frozen=True)
    last_name: str = Field(ge=2, le=25, frozen=True)


class RegistrationNumber(BaseModel):
    number: str = Field(pattern="(^8|7|\+7)((\d{10})|(\s\(\d{3}\)\s\d{3}\s\d{2}\s\d{2}))", frozen=True)


class RegistrationBirthday(BaseModel):
    birthday: datetime.datetime = DialogCalendar