from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from src.keyboards.fabric_method import Creator
from src.callback_fabrics.service import CallbackFabricService
from src.callback_fabrics.beauty_saloon import CallbackFabricBeautySaloon
from src.callback_fabrics.datetime_fabric import CallbackFabricDatetime
from src.callback_fabrics.specialist import CallbackFabricSpecialist
from src.states.appointment_state import Appointment
from src.keyboards.menu import gen_menu
from src.database.db_queries.user_queries import UserQueries

router = Router()


@router.callback_query(F.data == 'new_appointment')
async def new_appointment(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.set_state(Appointment.service)
    services = await Creator.factory('service').gen_menu(session=session, page=1)
    if services is None:
        await callback_query.answer('Услуг нет')
        await state.clear()
    else:
        await callback_query.message.edit_text('Выберите вид услуги', reply_markup=services)


@router.callback_query(Appointment.service, CallbackFabricService.filter(F.id))
async def service_appointment(callback_query: CallbackQuery, callback_data: CallbackFabricService, state: FSMContext,
                              session: AsyncSession):
    await state.update_data({"service_id": callback_data.id, "service_name": callback_data.name})
    await state.set_state(Appointment.beauty_saloon)
    beauty_saloons = await Creator.factory('beauty_saloon').gen_menu(session=session, service_id=int(callback_data.id), page=1)
    await callback_query.message.edit_text('Выберите салон красоты', reply_markup=beauty_saloons)


@router.callback_query(Appointment.beauty_saloon, CallbackFabricBeautySaloon.filter(F.id))
async def beauty_saloon_appointment(callback_query: CallbackQuery, callback_data: CallbackFabricBeautySaloon,
                                    state: FSMContext, session: AsyncSession):
    await state.update_data({"beauty_saloon_id": callback_data.id, 'beauty_saloon_name': callback_data.name})
    await state.set_state(Appointment.specialist)
    specialists = await Creator.factory('specialist').gen_menu(session=session, page=1, beauty_saloon_id=int(callback_data.id),
                                                               service_id=(await state.get_data())['service_id'])
    await callback_query.message.edit_text('Выберите специалиста', reply_markup=specialists)


@router.callback_query(Appointment.specialist, CallbackFabricSpecialist.filter(F.id))
async def specialist_appointment(callback_query: CallbackQuery, callback_data: CallbackFabricSpecialist,
                                 state: FSMContext, session: AsyncSession):
    await state.update_data({"specialist_id": callback_data.id, 'specialist_name': callback_data.name})
    await state.set_state(Appointment.date_appointment)
    datetimes = await Creator.factory('datetime').gen_menu(session=session, page=1, specialist_id=callback_data.id,
                                                           beauty_saloon_id=(await state.get_data())['beauty_saloon_id'],
                                                           service_id=(await state.get_data())['service_id']
                                                           )
    if datetimes is None:
        await callback_query.answer('Нет свободных записей')
        await gen_menu(session, callback_query.from_user.id, callback_query.message)
        await state.clear()
    else:
        await callback_query.message.edit_text('Выберите время записи', reply_markup=datetimes)


@router.callback_query(Appointment.date_appointment, CallbackFabricDatetime.filter(F.id))
async def datetime_appointment(callback_query: CallbackQuery, callback_data: CallbackFabricDatetime, state: FSMContext,
                               session: AsyncSession):
    try:
        await state.update_data({"datetime_id": callback_data.id, 'datetime_name': callback_data.name})
        await UserQueries.add_new_appointment(session, callback_query.from_user.id, callback_data.id)
        appointment_data = await state.get_data()
        await callback_query.message.edit_text(text=f'''Вы записались\nСалон: {appointment_data['beauty_saloon_name']}\nСпециалист: {appointment_data['specialist_name']}\nУслуга: {appointment_data['service_name']}\nВремя процедуры: {callback_data.name}''')
        await gen_menu(session, callback_query.from_user.id, callback_query.message)
        await state.clear()
    except Exception as e:
        print(e)
        pass
