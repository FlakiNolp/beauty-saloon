from aiogram.filters.callback_data import CallbackData


class CallbackFabricRemoveAppointment(CallbackData, prefix='remove_appointment'):
    appointment_id: int
