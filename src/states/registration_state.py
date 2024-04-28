from aiogram.fsm.state import State, StatesGroup


class RegistrationState(StatesGroup):
    user_type: State = State()


class UserRegistrationState(StatesGroup):
    names: State = State()
    number: State = State()
    birth_date: State = State()


class BeautySaloonRegistrationState(StatesGroup):
    name: State = State()
    number: State = State()
    address: State = State()