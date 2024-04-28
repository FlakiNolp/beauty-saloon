from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.database.models import BeautySaloon
from src.database.db_queries.beauty_saloon_queries import BeautySaloonQueries


async def gen_beauty_saloon_menu(session: AsyncSession, telegram_id: int, message: Message, new_message: bool = False) -> None:
    beauty_saloon = await BeautySaloonQueries.get_beauty_saloon_by_telegram_id(session, telegram_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Специалисты", callback_data='specialists')],
                                               [InlineKeyboardButton(text='Расписание', callback_data='time_table')],
                                               [InlineKeyboardButton(text='Посмотреть текущие записи', callback_data='current_appointments')],
                                               [InlineKeyboardButton(text='Посмотреть прошедшие записи', callback_data='archive_appointments')],
                                               [InlineKeyboardButton(text='Руководство пользователя', callback_data='help')]])
    try:
        if new_message:
            raise ValueError
        await message.edit_text(f'Управление салоном\nId: {telegram_id}\nНазвание: {beauty_saloon.name}\nНомер телефона: {beauty_saloon.number}\nАдрес: {beauty_saloon.address}', reply_markup=kb)
    except:
        await message.answer(f'Управление салоном\nId: {telegram_id}\nНазвание: {beauty_saloon.name}\nНомер телефона: {beauty_saloon.number}\nАдрес: {beauty_saloon.address}', reply_markup=kb)
