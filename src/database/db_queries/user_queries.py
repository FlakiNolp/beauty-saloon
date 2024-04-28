import datetime
from typing import Tuple, Any, Sequence
import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Row, func, delete

from src.database.models import User, Appointment, SaloonSpecService, BeautySaloon, Service, SaloonSpec, TimeSlot, \
    Specialist
import src.schemas as schemas


class UserQueries:
    @staticmethod
    async def add_new_user(session: AsyncSession, user: schemas.user.User):
        try:
            user = User(**user.model_dump())
            session.add(user)
            await session.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
            await session.rollback()

    @staticmethod
    async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User:
        try:
            return (await session.scalars(select(User).filter(User.telegram_id == telegram_id))).one()
        except sqlalchemy.exc.SQLAlchemyError as e:
            await session.rollback()
            raise e

    @staticmethod
    async def get_user_with_appointment_by_telegram_id(session: AsyncSession, telegram_id: int) -> Sequence[Row[
        Tuple[Any, Any, Any, Any, Any, Any, Any, Any, Any]]] | None:
        try:
            result = (await session.execute(
                select(BeautySaloon.name, BeautySaloon.number, BeautySaloon.address, Specialist.last_name,
                       Specialist.first_name, Service.name, SaloonSpecService.price, TimeSlot.date_time,
                       Appointment.id).select_from(
                    User).join(Appointment).join(TimeSlot).join(SaloonSpecService).join(Service).join(SaloonSpec).join(
                    BeautySaloon).join(Specialist).filter(User.telegram_id == telegram_id,
                                                          TimeSlot.date_time > datetime.datetime.now()))).all()
            return (await session.execute(
                select(BeautySaloon.name, BeautySaloon.number, BeautySaloon.address, Specialist.last_name,
                       Specialist.first_name, Service.name, SaloonSpecService.price, TimeSlot.date_time,
                       Appointment.id).select_from(
                    User).join(Appointment).join(TimeSlot).join(SaloonSpecService).join(Service).join(SaloonSpec).join(
                    BeautySaloon).join(Specialist).filter(User.telegram_id == telegram_id,
                                                          TimeSlot.date_time > datetime.datetime.now()))).all()
        except sqlalchemy.exc.SQLAlchemyError:
            await session.rollback()
            return None

    @staticmethod
    async def get_user_with_appointment_archive_by_telegram_id(session: AsyncSession, telegram_id: int) -> Sequence[Row[
        Tuple[Any, Any, Any, Any, Any, Any, Any, Any, Any]]] | None:
        try:
            return (await session.execute(
                select(BeautySaloon.name, BeautySaloon.number, BeautySaloon.address, Specialist.last_name,
                       Specialist.first_name, Service.name, SaloonSpecService.price, TimeSlot.date_time,
                       Appointment.id).select_from(
                    User).join(Appointment).join(TimeSlot).join(SaloonSpecService).join(Service).join(SaloonSpec).join(
                    BeautySaloon).join(Specialist).filter(User.telegram_id == telegram_id,
                                                          TimeSlot.date_time <= datetime.datetime.now()))).all()
        except sqlalchemy.exc.SQLAlchemyError:
            await session.rollback()
            return None

    @staticmethod
    async def get_number_of_services(session: AsyncSession) -> int | None:
        try:
            res = (await session.scalars(
                select(func.count()).select_from(Service).join(SaloonSpecService).join(TimeSlot).join(Appointment,
                                                                                                      isouter=True).
                filter(Appointment.time_slot_id == None, TimeSlot.date_time > datetime.datetime.now()))).first()
            return res
        except sqlalchemy.exc.SQLAlchemyError:
            await session.rollback()
            return None

    @staticmethod
    async def get_all_services(session: AsyncSession, limit: int, offset: int) -> Sequence[Service] | None:
        try:
            return (await session.scalars(select(Service).join(SaloonSpecService).join(TimeSlot).join(Appointment,
                                                                                                      isouter=True).
                                          filter(Appointment.time_slot_id == None, TimeSlot.date_time > datetime.datetime.now()).offset(offset).limit(limit))).unique().all()
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(e)
            await session.rollback()
            return None

    @staticmethod
    async def get_number_of_saloons_by_service(session: AsyncSession, service_id: int) -> int | None:
        try:
            return (await session.scalars(
                select(func.count()).select_from(BeautySaloon).join(SaloonSpec).join(Specialist).join(
                    SaloonSpecService).join(Service).join(TimeSlot).join(Appointment, isouter=True).filter(Service.id == service_id,
                                                                                            Appointment.time_slot_id == None, TimeSlot.date_time > datetime.datetime.now()))).first()
        except sqlalchemy.exc.SQLAlchemyError as e:
            await session.rollback()
            return None

    @staticmethod
    async def get_all_beauty_saloons_by_service(session: AsyncSession, service_id: int, limit: int, offset: int) -> \
            Sequence[BeautySaloon] | None:
        try:
            return (await session.scalars(
                select(BeautySaloon).join(SaloonSpec).join(SaloonSpecService).join(Service).join(TimeSlot).join(Appointment, isouter=True).select_from(
                    BeautySaloon).filter(Service.id == service_id, Appointment.time_slot_id == None, TimeSlot.date_time > datetime.datetime.now()).offset(offset).limit(limit))).unique().all()
        except sqlalchemy.exc.SQLAlchemyError as e:
            await session.rollback()
            return None

    @staticmethod
    async def get_number_of_specialist(session: AsyncSession, service_id: int, beauty_saloon_id: int) -> int | None:
        try:
            return (await session.scalars(
                select(func.count()).select_from(Specialist).join(SaloonSpec).join(BeautySaloon).join(
                    SaloonSpecService).join(TimeSlot).join(Appointment, isouter=True).join(Service).filter(Service.id == service_id,
                                                            BeautySaloon.id == beauty_saloon_id, Appointment.time_slot_id == None, TimeSlot.date_time > datetime.datetime.now()))).first()
        except sqlalchemy.exc.SQLAlchemyError as e:
            await session.rollback()
            return None

    @staticmethod
    async def get_all_specialists(session: AsyncSession, service_id: int, beauty_saloon_id: int, limit: int,
                                  offset: int) -> Sequence[Row[tuple[Specialist, Any]]] | None:
        try:
            return (await session.execute(
                select(Specialist, SaloonSpecService.price).join(SaloonSpec).join(BeautySaloon).join(SaloonSpecService)
                .join(Service).join(TimeSlot).join(Appointment, isouter=True).select_from(Specialist).filter(Service.id == service_id,
                                                              BeautySaloon.id == beauty_saloon_id, Appointment.time_slot_id == None, TimeSlot.date_time > datetime.datetime.now()).offset(
                    offset).limit(limit))).unique().all()
        except sqlalchemy.exc.SQLAlchemyError as e:
            await session.rollback()
            return None

    @staticmethod
    async def get_number_of_datetimes(session: AsyncSession, service_id: int, beauty_saloon_id: int,
                                      specialist_id: int) -> int | None:
        try:
            return (await session.scalars(
                select(func.count()).join(Appointment, isouter=True).join(SaloonSpecService).join(Service).join(SaloonSpec)
                .join(BeautySaloon).join(Specialist).select_from(TimeSlot).filter(
                    Service.id == service_id, BeautySaloon.id == beauty_saloon_id,
                    Specialist.id == specialist_id, Appointment.time_slot_id == None, TimeSlot.date_time > datetime.datetime.now()))).first()
        except sqlalchemy.exc.SQLAlchemyError as e:
            await session.rollback()
            return None

    @staticmethod
    async def get_all_datetimes(session: AsyncSession, service_id: int, beauty_saloon_id: int, specialist_id: int,
                                offset: int, limit: int) -> Sequence[TimeSlot] | None:
        try:
            return (await session.scalars(
                select(TimeSlot).join(Appointment, isouter=True).join(SaloonSpecService).join(Service).join(SaloonSpec)
                .join(BeautySaloon).join(Specialist).select_from(TimeSlot).filter(
                    Service.id == service_id,
                    BeautySaloon.id == beauty_saloon_id, Specialist.id == specialist_id,
                    Appointment.time_slot_id == None, TimeSlot.date_time > datetime.datetime.now()).offset(offset).limit(limit).order_by(TimeSlot.date_time))).unique().all()
        except sqlalchemy.exc.SQLAlchemyError as e:
            await session.rollback()
            return None

    @staticmethod
    async def add_new_appointment(session: AsyncSession, telegram_id: int, time_slot_id: int):
        try:
            appointment = Appointment(user_id=(await UserQueries.get_user_by_telegram_id(session, telegram_id)).id,
                                      time_slot_id=time_slot_id)
            session.add(appointment)
            await session.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
            await session.rollback()
            raise e

    @staticmethod
    async def delete_appointment(session: AsyncSession, appointment_id: int):
        try:
            query = delete(Appointment).filter(Appointment.id == appointment_id)
            await session.execute(query)
            await session.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
            await session.rollback()
            raise e
