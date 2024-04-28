from aiogram.fsm.state import State, StatesGroup


class Appointment(StatesGroup):
    service: State = State()
    beauty_saloon: State = State()
    specialist: State = State()
    date_appointment: State = State()
