import datetime
from typing import Tuple, Any, Sequence
import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Row, func, delete, cast, Date
from sqlalchemy.orm import load_only

from src.database.models import User, Appointment, SaloonSpecService, BeautySaloon, Service, SaloonSpec, TimeSlot, \
    Specialist
import src.schemas as schemas


class BeautySaloonQueries:
    @staticmethod
    async def add_new_beauty_saloon(session: AsyncSession, beauty_saloon: schemas.beauty_saloon.BeautySaloon):
        try:
            user = BeautySaloon(**beauty_saloon.model_dump())
            session.add(user)
            await session.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
            await session.rollback()

    @staticmethod
    async def get_beauty_saloon_by_telegram_id(session: AsyncSession, telegram_id: int) -> BeautySaloon:
        try:
            return (await session.scalars(select(BeautySaloon).filter(BeautySaloon.telegram_id == telegram_id))).one()
        except sqlalchemy.exc.SQLAlchemyError as e:
            await session.rollback()
            raise e

    @staticmethod
    async def get_user_with_appointment_by_telegram_id(session: AsyncSession, telegram_id: int) -> Sequence[Row[
        Tuple[Any, Any, Any, Any, Any, Any, Any, Any]]] | None:
        try:
            return (await session.execute(
                select(User.last_name, User.first_name, User.number, Specialist.last_name, Specialist.first_name,
                       Service.name, SaloonSpecService.price, TimeSlot.date_time).select_from(
                    BeautySaloon).join(SaloonSpec).join(Specialist).join(SaloonSpecService).join(Service).join(
                    TimeSlot).join(
                    Appointment).join(User).filter(BeautySaloon.telegram_id == telegram_id,
                                                   TimeSlot.date_time > datetime.datetime.now()))).unique().all()
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(e)
            await session.rollback()
            return None

    @staticmethod
    async def get_user_with_appointment_archive_by_telegram_id(session: AsyncSession, telegram_id: int) -> Sequence[Row[
        Tuple[Any, Any, Any, Any, Any, Any, Any, Any]]] | None:
        try:
            return (await session.execute(
                select(User.last_name, User.first_name, User.number, Specialist.last_name, Specialist.first_name,
                       Service.name,
                       SaloonSpecService.price, TimeSlot.date_time).select_from(
                    BeautySaloon).join(SaloonSpec).join(Specialist).join(SaloonSpecService).join(Service).join(
                    TimeSlot).join(
                    Appointment).join(User).filter(BeautySaloon.telegram_id == telegram_id,
                                                   TimeSlot.date_time <= datetime.datetime.now()))).unique().all()
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(e)
            await session.rollback()
            return None

    @staticmethod
    async def get_specialists(session: AsyncSession, telegram_id: int) -> Sequence[Specialist] | None:
        try:
            return (await session.scalars(
                select(Specialist).join(SaloonSpec).join(Specialist).select_from(BeautySaloon).filter(
                    BeautySaloon.telegram_id == telegram_id))).unique().all()
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(e)
            await session.rollback()
            return None

    @staticmethod
    async def delete_specialist(session: AsyncSession, specialist_id: int) -> None:
        try:
            await session.execute(delete(Specialist).where(Specialist.id == specialist_id))
            await session.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(e)
            await session.rollback()

    @staticmethod
    async def add_specialist(session: AsyncSession, telegram_id: int,
                             specialist: schemas.beauty_saloon.Specialist) -> None:
        try:
            specialist = Specialist(**specialist.model_dump())
            session.add(specialist)
            await session.flush([specialist])
            saloon_spec = SaloonSpec(
                beauty_saloon_id=(await BeautySaloonQueries.get_beauty_saloon_by_telegram_id(session, telegram_id)).id,
                specialist_id=specialist.id)
            session.add(saloon_spec)
            await session.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(e)
            await session.rollback()

    @staticmethod
    async def get_time_table(session: AsyncSession, telegram_id: int, date_time: datetime) -> Sequence[
        Row[Tuple[Any, Any, Any, Any, Any, Any, Any]]]:
        try:
            return (await session.execute(
                select(Specialist.last_name, Specialist.first_name, Service.name, SaloonSpecService.price,
                       func.min(TimeSlot.date_time).label('start_time'), func.max(TimeSlot.date_time).label('end_time'),
                       func.count(TimeSlot.date_time).label('number_of_time_slots'))
                .select_from(TimeSlot).join(SaloonSpecService).join(Service).join(SaloonSpec).join(Specialist).join(
                    BeautySaloon)
                .filter(BeautySaloon.telegram_id == telegram_id,
                        date_time < TimeSlot.date_time,
                        TimeSlot.date_time < date_time + datetime.timedelta(days=1))
                .group_by(Specialist.last_name, Specialist.first_name, Service.name, SaloonSpecService.price)
                .order_by('start_time'))).unique().all()
        except sqlalchemy.exc.SQLAlchemyError as e:
            await session.rollback()
            print(e)

    @staticmethod
    async def get_services(session: AsyncSession) -> Sequence[Service]:
        try:
            return (await session.scalars(select(Service))).unique().all()
        except sqlalchemy.exc.SQLAlchemyError as e:
            await session.rollback()
            print(e)

    @staticmethod
    async def get_saloon_spec(session: AsyncSession, specialist_id: int) -> SaloonSpec | None:
        try:
            return (await session.scalars(
                select(SaloonSpec).filter(SaloonSpec.specialist_id == specialist_id))).unique().one()
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(e)
            await session.rollback()
            return None

    @staticmethod
    async def get_saloon_service_spec(session: AsyncSession, service_id: int, saloon_spec_id: int):
        try:
            return (await session.scalars(select(SaloonSpecService).filter(SaloonSpecService.service_id == service_id,
                                                                           SaloonSpecService.saloon_spec_id == saloon_spec_id))).unique().one()
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(e)
            return None

    @staticmethod
    async def update_time_table(session: AsyncSession, telegram_id: int, specialist_id: int, services: dict,
                                date_times: list[datetime.datetime]) -> None:
            saloon_spec_services = list()
            for key, value in services.items():
                saloon_spec = (await BeautySaloonQueries.get_saloon_spec(session, specialist_id)).id
                if (saloon_spec_service := await BeautySaloonQueries.get_saloon_service_spec(session, key, saloon_spec)) is None:
                    saloon_spec_services.append(SaloonSpecService(price=str(value), service_id=key,
                                                                  saloon_spec_id=saloon_spec))
                    session.add_all(saloon_spec_services)
                    await session.flush(saloon_spec_services)
                else:
                    saloon_spec_services.append(saloon_spec_service)
            time_tables = list()
            for saloon_spec_service in saloon_spec_services:
                [time_tables.append(TimeSlot(date_time=date_time, saloon_spec_service_id=saloon_spec_service.id)) for
                 date_time in date_times]
            session.add_all(time_tables)
            await session.commit()

    @staticmethod
    async def get_exist_dates(session: AsyncSession, telegram_id):
        try:
            return (await session.execute(select(cast(TimeSlot.date_time, Date)).select_from(BeautySaloon).join(SaloonSpec)
                                          .join(SaloonSpecService).join(TimeSlot).filter(BeautySaloon.telegram_id == telegram_id))).unique().all()
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(e)
            return None

