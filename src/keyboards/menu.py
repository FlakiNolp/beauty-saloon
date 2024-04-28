from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from src.database.models import User
from src.database.db_queries.user_queries import UserQueries


async def gen_menu(session: AsyncSession, telegram_id: int, message: Message) -> None:
    user = await UserQueries.get_user_by_telegram_id(session, telegram_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Записаться", callback_data='new_appointment'),
                              InlineKeyboardButton(text='Активные записи', callback_data='my_appointment')],
                                               [InlineKeyboardButton(text='Прошедшие записи', callback_data='archive')],
                                               [InlineKeyboardButton(text='Руководство пользователя', callback_data='help')]])
    try:
        await message.edit_text(f'Личный кабинет\nId: {telegram_id}\nФамилия: {user.last_name}\nИмя: {user.first_name}\nНомер телефона: {user.number}\nДата рождения: {user.birthday}', reply_markup=kb)
    except:
        await message.answer(f'Личный кабинет\nId: {telegram_id}\nФамилия: {user.last_name}\nИмя: {user.first_name}\nНомер телефона: {user.number}\nДата рождения: {user.birthday}', reply_markup=kb)
