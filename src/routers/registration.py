from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import aiogram.types as aiogram_types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, \
    InlineKeyboardMarkup
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from src.states.registration_state import UserRegistrationState, BeautySaloonRegistrationState
from src.aiogram_calendar import DialogCalendar, get_user_locale, DialogCalendarCallback
from src.database.db_queries.user_queries import UserQueries
from src.database.db_queries.beauty_saloon_queries import BeautySaloonQueries
import src.schemas as schemas
from src.keyboards.menu import gen_menu
from src.keyboards.beauty_saloon_menu import gen_beauty_saloon_menu

router = Router()


@router.message(CommandStart())
async def start(message: aiogram_types.Message):
    await message.answer(
        "Привет, я бот для упрощения взаимодействия между клиентами и салонов красоты. Давай знакомиться. Кто ты?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Пользователь", callback_data='user'),
                              InlineKeyboardButton(text="Салон красоты", callback_data="saloon")]],
            resize_keyboard=True, one_time_keyboard=True),
    )


@router.callback_query(F.data == "user")
async def register_user(callback: aiogram_types.CallbackQuery, state: FSMContext):
    await state.set_state(UserRegistrationState.names)
    await callback.message.edit_text("Напишите свои фамилию и имя. Например Иванов Иван")


@router.message(UserRegistrationState.names)
async def register_user_names(message: aiogram_types.Message, state: FSMContext):
    try:
        message_user = message.text.title().split()
        if len(message_user) != 2:
             raise ValueError('Неверный формат')
        schemas.user.User.model_validate({'telegram_id': message.from_user.id, 'first_name': message_user[1], 'last_name': message_user[0]})
        await state.update_data({"first_name": message_user[1], "last_name": message_user[0]})
        await state.set_state(UserRegistrationState.number)
        await message.answer("Нам нужен номер телефона для записи, поделитесь им, нажав на кнопку снизу",
                             reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(
                                 text="Поделиться номером", request_contact=True)]], resize_keyboard=True,
                                 one_time_keyboard=True))
    except ValidationError as e:
        print(e)
        await message.answer(str(e))
    except ValueError as e:
        await message.answer(str(e))
    except Exception as e:
        await message.answer('Непридвиденная ошибка')


@router.message(F.contact, UserRegistrationState.number)
async def register_user_number(message: aiogram_types.Message, state: FSMContext):
    await state.update_data({"number": message.contact.phone_number})
    await state.set_state(UserRegistrationState.birth_date)
    dc = DialogCalendar(locale=await get_user_locale(message.from_user))
    dc.set_dates_range(datetime.datetime.today() - datetime.timedelta(days=4745), datetime.datetime.today())
    await message.answer('Выберите дату рождения',
                         reply_markup=await dc.start_calendar((datetime.datetime.today() - datetime.timedelta(days=6570)).year))


@router.callback_query(DialogCalendarCallback.filter(), UserRegistrationState.birth_date)
async def register_user_birthday(callback_query: aiogram_types.CallbackQuery, callback_data: CallbackData, state: FSMContext,
                                 session: AsyncSession):
    selected, date = await DialogCalendar(
        locale=await get_user_locale(callback_query.from_user)
    ).process_selection(callback_query, callback_data)
    if selected:
        try:
            if date <= datetime.datetime.today() - datetime.timedelta(days=4745):
                await state.update_data({"birthday": date})
                datas = await state.get_data()
                datas['telegram_id'] = callback_query.from_user.id
                await UserQueries.add_new_user(session, user=schemas.user.User(**datas))
                await gen_menu(session, callback_query.from_user.id, callback_query.message)
            else:
                await callback_query.message.answer('Вам должно быть больше 16 лет')
        except ValidationError:
            await callback_query.message.answer('')


@router.callback_query(F.data == 'saloon')
async def register_saloon(callback: aiogram_types.CallbackQuery, state: FSMContext):
    await state.set_state(BeautySaloonRegistrationState.name)
    await callback.message.answer('Напишите название салона')


@router.message(BeautySaloonRegistrationState.name)
async def register_saloon_name(message: aiogram_types.Message, state: FSMContext):
    try:
        message_user = message.text
        if len(message_user) > 50:
            raise ValueError('Слишком длинные название')
        elif not message_user.isalpha():
            raise ValueError('Фамилия и имя должны содержать только буквы')
        await state.update_data({"name": message_user})
        await state.set_state(BeautySaloonRegistrationState.number)
        await message.answer("Нам нужен номер телефона для возможности контакта с пользователями. Напишите его, пожалуйста в формате +7900000000")
    except ValueError as e:
        await message.answer(str(e))
    except Exception as e:
        await message.answer('Непридвиденная ошибка')


@router.message(BeautySaloonRegistrationState.number)
async def register_saloon_number(message: aiogram_types.Message, state: FSMContext):
    try:
        number = message.text
        schemas.registration_models.RegistrationNumber.model_validate({"number": number})
        await state.update_data({'number': number})
        await state.set_state(BeautySaloonRegistrationState.address)
        await message.answer('И последнее адрес вашего салона')
    except ValidationError:
        await message.answer('Неверный формат номера телефона')


@router.message(BeautySaloonRegistrationState.address)
async def register_saloon_address(message: aiogram_types.Message, state: FSMContext, session: AsyncSession):
    try:
        address = message.text
        if len(address) > 200:
            raise ValueError('Слишком длинный адрес')
        await state.update_data({'address': address, "telegram_id": message.from_user.id})
        datas = await state.get_data()
        await BeautySaloonQueries.add_new_beauty_saloon(session=session,
                                                        beauty_saloon=schemas.beauty_saloon.BeautySaloon(**datas))
        await gen_beauty_saloon_menu(session, message.from_user.id, message)
    except ValueError as e:
        await message.answer('Непридвиденная ошибка')
        await message.answer(str(e))





