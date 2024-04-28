import datetime

from pydantic import BaseModel, field_validator, Field


class User(BaseModel):
    telegram_id: int = Field()
    first_name: str = Field(min_length=2, max_length=25, pattern='[A-Za-zа-яА-ЯёЁ]')
    last_name: str = Field(min_length=2, max_length=25, pattern='[A-Za-zа-яА-ЯёЁ]')
    number: str = Field(default='', pattern='(^8|7|\+7)((\d{10})|(\s\(\d{3}\)\s\d{3}\s\d{2}\s\d{2}))')
    birthday: datetime.date = Field(default=datetime.date.today)

    @field_validator('birthday')
    def birthday_validator(cls, v):
        if v >= datetime.date.today():
            raise ValueError("Birthday cannot be in the future")
        return v
