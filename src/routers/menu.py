from aiogram.enums import ParseMode
from aiogram.filters import Command
import aiogram.types as aiogram_types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types.input_file import FSInputFile

from src.keyboards.beauty_saloon_menu import gen_beauty_saloon_menu
from src.database.db_queries.beauty_saloon_queries import BeautySaloonQueries
from src.callback_fabrics.remove_appointment import CallbackFabricRemoveAppointment
from src.keyboards.fabric_method import Creator
from src.callback_fabrics.switch import CallbackFabricSwitch
from src.states.appointment_state import Appointment
from src.keyboards.menu import gen_menu
from src.database.db_queries.user_queries import UserQueries

router = Router()


@router.message(Command('user'))
async def menu(message: aiogram_types.Message, session: AsyncSession, state: FSMContext):
    try:
        await gen_menu(session, message.from_user.id, message)
        await state.clear()
    except Exception as e:
        print(e)
        await message.answer('Вам нужно зарегистрироваться')


@router.message(Command('salon'))
async def menu(message: aiogram_types.Message, session: AsyncSession, state: FSMContext):
    try:
        await gen_beauty_saloon_menu(session, message.from_user.id, message)
        await state.clear()
    except Exception as e:
        print(e)
        await message.answer('Вам нужно зарегистрироваться')


@router.callback_query(F.data == 'my_appointment')
async def my_appointment(callback_query: aiogram_types.CallbackQuery, session: AsyncSession):
    try:
        appointments = await UserQueries.get_user_with_appointment_by_telegram_id(session, callback_query.from_user.id)
        if appointments:
            for i in appointments:
                await callback_query.message.answer(f'{i[0]} {i[1]} {i[2]}\n{i[3]} {i[4]}\n{i[5]} {i[6]}\n{i[7]}',
                                                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                        [InlineKeyboardButton(text='❌ Отменить запись',
                                                                              callback_data=CallbackFabricRemoveAppointment(appointment_id=i[8]).pack())]]))
            await gen_menu(session, callback_query.from_user.id, callback_query.message)
        else:
            await callback_query.answer('У вас нет записей')
    except Exception as e:
        print(e)
        await callback_query.message.answer('Вам нужно зарегистрироваться')


@router.callback_query(F.data == 'archive')
async def my_archive(callback_query: aiogram_types.CallbackQuery, session: AsyncSession):
    try:
        appointments = await UserQueries.get_user_with_appointment_archive_by_telegram_id(session, callback_query.from_user.id)
        if appointments:
            for i in appointments:
                await callback_query.message.answer(f'{i[0]} {i[1]} {i[2]}\n{i[3]} {i[4]}\n{i[5]} {i[6]}\n{i[7]}')
            await gen_menu(session, callback_query.from_user.id, callback_query.message)
        else:
            await callback_query.answer('У вас нет записей')
    except Exception as e:
        print(e)
        await callback_query.message.answer('Вам нужно зарегистрироваться')


@router.callback_query(CallbackFabricRemoveAppointment.filter(F.appointment_id))
async def delete_appointment(callback_query: aiogram_types.CallbackQuery, callback_data: CallbackFabricRemoveAppointment,
                             session: AsyncSession):
    try:
        await UserQueries.delete_appointment(session, callback_data.appointment_id)
        await callback_query.message.edit_text('**Запись отменена** ✅', parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        print(e)
        await callback_query.answer('Непридвидинная ошибка')


@router.callback_query(F.data == 'current_appointments')
async def current_appointment(callback_query: aiogram_types.CallbackQuery, session: AsyncSession):
    try:
        appointments = await BeautySaloonQueries.get_user_with_appointment_by_telegram_id(session, callback_query.from_user.id)
        if appointments:
            for i in appointments:
                await callback_query.message.answer(f'{i[0]} {i[1]} {i[2]}\n{i[3]} {i[4]}\n{i[5]} {i[6]}\n{i[7]}')
            await gen_beauty_saloon_menu(session, callback_query.from_user.id, callback_query.message)
        else:
            await callback_query.answer('К вам нет записей')
    except Exception as e:
        print(e)
        await callback_query.message.answer('Вам нужно зарегистрироваться')


@router.callback_query(F.data == 'archive_appointments')
async def current_appointment(callback_query: aiogram_types.CallbackQuery, session: AsyncSession):
    try:
        appointments = await BeautySaloonQueries.get_user_with_appointment_archive_by_telegram_id(session, callback_query.from_user.id)
        if appointments:
            for i in appointments:
                await callback_query.message.answer(f'{i[0]} {i[1]} {i[2]}\n{i[3]} {i[4]}\n{i[5]} {i[6]}\n{i[7]}')
            await gen_beauty_saloon_menu(session, callback_query.from_user.id, callback_query.message)
        else:
            await callback_query.answer('У вас нет записей')
    except Exception as e:
        print(e)
        await callback_query.message.answer('Вам нужно зарегистрироваться')


@router.callback_query(CallbackFabricSwitch.filter(F.direction == '>'))
async def right(callback_query: CallbackQuery, callback_data: CallbackFabricSwitch, session: AsyncSession, state: FSMContext):
    services = await Creator.factory(callback_data.type).gen_menu(session=session, page=callback_data.page + 1, **await state.get_data())
    await callback_query.message.edit_reply_markup('Выберите вид услуги', reply_markup=services)


@router.callback_query(CallbackFabricSwitch.filter(F.direction == '<'))
async def left(callback_query: CallbackQuery, callback_data: CallbackFabricSwitch, session: AsyncSession, state: FSMContext):
    services = await Creator.factory(callback_data.type).gen_menu(session=session, page=callback_data.page - 1, **await state.get_data())
    await callback_query.message.edit_reply_markup('Выберите вид услуги', reply_markup=services)


@router.callback_query(CallbackFabricSwitch.filter(F.direction == 'back'))
async def back(callback_query: CallbackQuery, callback_data: CallbackFabricSwitch, state: FSMContext, session: AsyncSession):
    if callback_data.type == 'service':
        await state.clear()
        await gen_menu(session, callback_query.from_user.id, callback_query.message)
    elif callback_data.type == 'beauty_saloon':
        kb = await Creator.factory('service').gen_menu(session=session, page=1)
        await state.set_state(Appointment.service)
        await callback_query.message.edit_text(text='Выберите тип услуги', reply_markup=kb)
    elif callback_data.type == 'specialist':
        kb = await Creator.factory('beauty_saloon').gen_menu(session=session, page=1, service_id=(await state.get_data())['service_id'])
        await state.set_state(Appointment.beauty_saloon)
        await callback_query.message.edit_text('Выберите салон красоты', reply_markup=kb)
    elif callback_data.type == 'datetime':
        kb = await Creator.factory('specialist').gen_menu(session=session, page=1,
                                                          service_id=(await state.get_data())['service_id'],
                                                          beauty_saloon_id=(await state.get_data())['beauty_saloon_id'])
        await state.set_state(Appointment.specialist)
        await callback_query.message.edit_text('Выберите специалиста', reply_markup=kb)
    elif callback_data.type == 'specialists':
        await gen_beauty_saloon_menu(session, callback_query.from_user.id, callback_query.message)


@router.callback_query(F.data == 'help')
async def help_handler(callback_query: CallbackQuery):
    file = FSInputFile(path=r'C:\Users\maksi\PycharmProjects\Daria_telegram_bot\src\routers\help.pdf')
    await callback_query.message.answer_document(document=file)

