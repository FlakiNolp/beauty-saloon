from pydantic import BaseModel, Field


class BeautySaloon(BaseModel):
    telegram_id: int = Field()
    name: str = Field(min_length=2, max_length=50)
    number: str = Field(pattern='(^8|7|\+7)((\d{10})|(\s\(\d{3}\)\s\d{3}\s\d{2}\s\d{2}))')
    address: str = Field(min_length=2, max_length=200)


class Specialist(BaseModel):
    last_name: str = Field(min_length=2, max_length=25)
    first_name: str = Field(min_length=2, max_length=25)
    experience: int = Field(default=0, ge=0, le=100)
