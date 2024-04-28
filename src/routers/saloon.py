from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, \
    InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError
from collections import defaultdict

from src.keyboards.fabric_method import Creator
from src.callback_fabrics.service import CallbackFabricService
from src.callback_fabrics.remove_specialist import CallbackFabricRemoveSpecialist
from src.callback_fabrics.datetime_fabric import CallbackFabricDatetime
from src.callback_fabrics.service import CallbackFabricService
from src.callback_fabrics.specialist import CallbackFabricSpecialist
from src.callback_fabrics.switch import CallbackFabricSwitch
from src.states.add_spec_state import AddSpecialistState
from src.states.add_time_table_state import AddTimeTableState
from src.states.current_time_table_state import CurrentTimeTableState
from src.keyboards.beauty_saloon_menu import gen_beauty_saloon_menu
from src.database.db_queries.beauty_saloon_queries import BeautySaloonQueries
import src.schemas as schemas
from src.aiogram_calendar.dialog_calendar import DialogCalendar, DialogCalendarCallback
from src.aiogram_calendar.common import get_user_locale

router = Router()


@router.callback_query(F.data == 'specialists')
async def specialists_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Добавить специалиста', callback_data='add_specialist')],
                         [InlineKeyboardButton(text='Специалисты', callback_data='get_specialists')],
                         [InlineKeyboardButton(text='Назад',
                                               callback_data=CallbackFabricSwitch(direction='back', page=1,
                                                                                  type='specialists').pack())]]))


@router.callback_query(F.data == 'get_specialists')
async def get_specialists(callback_query: CallbackQuery, session: AsyncSession):
    specialists = await BeautySaloonQueries.get_specialists(session, telegram_id=callback_query.from_user.id)
    if specialists:
        for i in specialists:
            await callback_query.message.answer(f'Фамилия: {i.last_name}\nИмя: {i.first_name}\nОпыт: {i.experience}',
                                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                    [InlineKeyboardButton(text='❌ Удалить специалиста',
                                                                          callback_data=CallbackFabricRemoveSpecialist(
                                                                              specialist_id=str(i.id)).pack())]]))
        await gen_beauty_saloon_menu(session, callback_query.from_user.id, callback_query.message, new_message=True)
        await callback_query.message.delete()
    else:
        await callback_query.answer('У вас нет специалистов')


@router.callback_query(CallbackFabricRemoveSpecialist.filter(F.specialist_id))
async def delete_specialist(callback_query: CallbackQuery, callback_data: CallbackFabricRemoveSpecialist,
                            session: AsyncSession):
    await BeautySaloonQueries.delete_specialist(session, callback_data.specialist_id)
    await callback_query.message.edit_text('**Работник уволен** ✅', parse_mode=ParseMode.MARKDOWN_V2)


@router.callback_query(F.data == 'add_specialist')
async def add_specialist(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(AddSpecialistState.names)
    await callback_query.message.answer('Напишите фамилию и имя специалиста. Например Иванов Иван')


@router.message(AddSpecialistState.names)
async def add_specialist_names(message: Message, state: FSMContext):
    try:
        names = message.text.title().split()
        if len(names) != 2:
            raise ValueError('Неверный формат')
        schemas.beauty_saloon.Specialist.model_validate({'first_name': names[1], 'last_name': names[0]})
        await state.update_data({"first_name": names[1], "last_name": names[0]})
        await state.set_state(AddSpecialistState.experience)
        await message.answer("Напишите опыт специалиста в годах",
                             reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(
                                 text=str(i)) for i in range(1 + (j * 3), 4 + (j * 3))] for j in range(0, 10)],
                                 resize_keyboard=True,
                                 one_time_keyboard=True))
    except ValidationError as e:
        print(e)
    except ValueError as e:
        await message.answer(str(e))
    except Exception as e:
        await message.answer('Непридвиденная ошибка')


@router.message(AddSpecialistState.experience)
async def add_specialist_experience(message: Message, session: AsyncSession, state: FSMContext):
    try:
        experience = message.text
        if not experience.isdigit():
            return ValueError('Опыт должен быть числом')
        experience = int(experience)
        schemas.beauty_saloon.Specialist.model_validate({'experience': experience,
                                                         'first_name': (await state.get_data())['first_name'],
                                                         'last_name': (await state.get_data())['last_name']})
        await state.update_data({"experience": experience})
        await BeautySaloonQueries.add_specialist(session, message.from_user.id,
                                                 schemas.beauty_saloon.Specialist(**await state.get_data()))
        await message.answer('Специалист добавлен 💅')
        await gen_beauty_saloon_menu(session, message.from_user.id, message)
    except ValidationError as e:
        print(e)
        await message.answer('Число должно быть в промежутке от 0 до 100')
    except ValueError as e:
        await message.answer(str(e))
    except Exception as e:
        print(e)
        await message.answer('Непридвиденная ошибка')


@router.callback_query(F.data == 'time_table')
async def time_table(callback_query: CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Текущее расписание', callback_data='current_time_table')],
                         [InlineKeyboardButton(text='Добавить расписание', callback_data='add_time_table')]]))


@router.callback_query(F.data == 'current_time_table')
async def current_time_table(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.set_state(CurrentTimeTableState.date)
    exits_dates = await BeautySaloonQueries.get_exist_dates(session, telegram_id=callback_query.from_user.id)
    dc = DialogCalendar(locale=await get_user_locale(callback_query.from_user), exist_dates=exits_dates)
    await callback_query.message.edit_text('Выберите дату',
                                           reply_markup=await dc.start_calendar(year=datetime.datetime.today().year,
                                                                                month=datetime.datetime.today().month))


@router.callback_query(DialogCalendarCallback.filter(), CurrentTimeTableState.date)
async def current_time_table_date(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext,
                                  session: AsyncSession):
    selected, date = await DialogCalendar(
        locale=await get_user_locale(callback_query.from_user)
    ).process_selection(callback_query, callback_data)
    if selected:
        try:
            time_tables = await BeautySaloonQueries.get_time_table(session, callback_query.from_user.id, date_time=date)
            if time_tables:
                for i in time_tables:
                    await callback_query.message.answer(
                        f'{i[0]} {i[1]}\n{i[2]} {i[3]}\nНачал смены: {i[4]}\nКонец смены: {i[5] + (i[5] - i[4]) / (i[6] - 1)}\nПромежутки между записями: {(i[5] - i[4]) / (i[6] - 1) if i[6] > 1 else i[5] - i[4]}')
            else:
                await callback_query.message.answer('На этот день расписания нет')
            await gen_beauty_saloon_menu(session, callback_query.from_user.id, callback_query.message, new_message=True)
            await callback_query.message.delete()
            await state.clear()
        except ValidationError:
            await callback_query.message.answer('')


@router.callback_query(F.data == 'add_time_table')
async def add_time_table(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    specialists = await BeautySaloonQueries.get_specialists(session, callback_query.from_user.id)
    if not specialists:
        await callback_query.answer('Добавьте специалистов')
    else:
        kb = InlineKeyboardBuilder()
        for i in specialists:
            kb.add(InlineKeyboardButton(text=i.last_name,
                                        callback_data=CallbackFabricSpecialist(name=f'{i.last_name} {i.first_name}',
                                                                               id=i.id).pack()))
        await state.set_state(AddTimeTableState.specialist)
        await callback_query.message.edit_text(text='Выберите специалиста, кототорому хотите добавить расписание смены',
                                               reply_markup=kb.as_markup())


@router.callback_query(AddTimeTableState.specialist, CallbackFabricSpecialist.filter(F.id))
async def add_time_table_specialist(callback_query: CallbackQuery, state: FSMContext,
                                    callback_data: CallbackFabricSpecialist):
    await state.update_data({'specialist_id': callback_data.id, 'specialist_name': callback_data.name})
    await state.set_state(AddTimeTableState.date)
    dc = DialogCalendar(locale=await get_user_locale(callback_query.from_user))
    await callback_query.message.edit_text(
        f'{callback_data.name}\n\nВыберите дату, на которую нужно составить расписание',
        reply_markup=await dc.start_calendar(year=datetime.datetime.today().year,
                                             month=datetime.datetime.today().month))


@router.callback_query(DialogCalendarCallback.filter(), AddTimeTableState.date)
async def add_time_table_date(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext,
                              session: AsyncSession):
    selected, date = await DialogCalendar(
        locale=await get_user_locale(callback_query.from_user)
    ).process_selection(callback_query, callback_data)
    if selected:
        try:
            if date > datetime.datetime.today():
                services = await BeautySaloonQueries.get_services(session)
                kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=service.name,
                                                                                 callback_data=CallbackFabricService(
                                                                                     id=service.id,
                                                                                     name=service.name).pack())] for
                                                           service in services])
                await state.update_data({"date": date})
                datas = await state.get_data()
                await state.set_state(AddTimeTableState.services)
                kb.inline_keyboard.append([InlineKeyboardButton(text='Больше не нужно', callback_data='end_service')])
                await callback_query.message.edit_text(
                    f'{datas['specialist_name']}\n{datas['date'].date()}\n\nВыберите услугу',
                    reply_markup=kb)
            else:
                await callback_query.message.answer('Расписание можно составить только на будущее')
        except ValidationError:
            await callback_query.message.answer('')


@router.callback_query(AddTimeTableState.services, CallbackFabricService.filter(F.id))
async def add_time_table_services(callback_query: CallbackQuery, state: FSMContext,
                                  callback_data: CallbackFabricService):
    datas = await state.get_data()
    await state.update_data({"service_id": callback_data.id, 'service_name': callback_data.name})
    await state.set_state(AddTimeTableState.price)
    await callback_query.message.edit_text(
        f'{datas['specialist_name']}\n{datas['date'].date()}\n\nНапишите цену для {callback_data.name}', )


@router.message(AddTimeTableState.price)
async def add_time_table_price(message: Message, state: FSMContext, session: AsyncSession):
    price = float(message.text)
    await state.update_data({"price": price})
    datas = await state.get_data()
    if datas.get('services'):
        services: dict = datas['services']
        services.update({datas['service_id']: price})
        await state.update_data({"services": services})
    else:
        await state.update_data({"services": {datas['service_id']: price}})
    services = await BeautySaloonQueries.get_services(session)
    #kb = InlineKeyboardBuilder()
    datas = await state.get_data()
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=f'{i.name} - {price} ✅', callback_data='nothing')]
                         if i.id in datas['services'].keys() else [InlineKeyboardButton(text=i.name,
                                                                                        callback_data=CallbackFabricService(
                                                                                            id=i.id,
                                                                                            name=i.name).pack())] for i
                         in
                         services])
    kb.inline_keyboard.append([InlineKeyboardButton(text='Больше не нужно', callback_data='end_service')])
    await state.set_state(AddTimeTableState.services)
    await message.answer(f'{datas['specialist_name']}\n{datas['date'].date()}', reply_markup=kb)


@router.callback_query(AddTimeTableState.services, F.data == 'end_service')
async def end_service(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(AddTimeTableState.start_time)
    await callback_query.message.edit_text('Напишите начало смены. Например в 10:00')


@router.message(AddTimeTableState.start_time)
async def start_time(message: Message, state: FSMContext):
    try:
        time_from = datetime.datetime.strptime(message.text, '%H:%M').time()
        time_from = (await state.get_data())['date'] + datetime.timedelta(hours=time_from.hour, minutes=time_from.minute)
        await state.update_data({'start_time': time_from})
        print(time_from.hour, time_from.day * 24)
        await state.set_state(AddTimeTableState.end_time)
        await message.answer('Напишите конец смены. Например в 18:00')
    except:
        await message.answer('Формат должен быть строго 00:00')


@router.message(AddTimeTableState.end_time)
async def end_time(message: Message, state: FSMContext):
    try:
        time_to = datetime.datetime.strptime(message.text, '%H:%M').time()
        time_to = (await state.get_data())['date'] + datetime.timedelta(hours=time_to.hour, minutes=time_to.minute)
        await state.update_data({'end_time': time_to})
        await state.set_state(AddTimeTableState.period_time)
        await message.answer('Напишите разницу между записями. Например в 01:15 или 00:30 часа')
    except:
        await message.answer('Формат должен быть строго 00:00')


@router.message(AddTimeTableState.period_time)
async def period_time(message: Message, state: FSMContext, session: AsyncSession):
    try:
        period = datetime.datetime.strptime(message.text, '%H:%M').time()
        await state.update_data({'period_time': period})
        datas = await state.get_data()
        period = (lambda start, end, period: [start + datetime.timedelta(minutes=i) for i in
                                              range(0, int((end - start - datetime.timedelta(hours=period.hour,
                                                                                             minutes=period.minute)).total_seconds() / 60),
                                                    period.hour * 60 + period.minute)])(datas['start_time'],
                                                                                        datas['end_time'],
                                                                                        datas['period_time'])
        await BeautySaloonQueries.update_time_table(session=session, telegram_id=message.from_user.id,
                                                    specialist_id=datas['specialist_id'], services=datas['services'],
                                                    date_times=period)
        await message.answer('Расписание успешно добавлено')
        await gen_beauty_saloon_menu(session, message.from_user.id, message)
    except Exception as e:
        print(e)
        await message.answer('Формат должен быть строго 00:00')
