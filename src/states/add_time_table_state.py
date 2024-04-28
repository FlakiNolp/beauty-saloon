from aiogram.fsm.state import State, StatesGroup


class AddTimeTableState(StatesGroup):
    specialist: State = State()
    date: State = State()
    services: State = State()
    price: State = State()
    start_time: State = State()
    end_time: State = State()
    period_time: State = State()