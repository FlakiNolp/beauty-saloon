import decimal
from sqlalchemy import ForeignKey, String, SmallInteger
from sqlalchemy.dialects.postgresql import MONEY
from sqlalchemy.orm import relationship, Mapped, DeclarativeBase, mapped_column
from typing import List
import datetime


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, comment="ID сущности")


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "public"}
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(length=25), nullable=False, comment="Имя пользователя")
    last_name: Mapped[str] = mapped_column(String(length=25), nullable=False, comment="Фамилия пользователя")
    number: Mapped[str] = mapped_column(nullable=False, unique=True, comment="Номер телефона пользователя")
    birthday: Mapped[datetime.date] = mapped_column(nullable=False, comment="День рожденния пользователя")
    appointments: Mapped[List['Appointment']] = relationship(back_populates="user", lazy="selectin", cascade="all, delete", passive_deletes=True, passive_updates=True)


class BeautySaloon(Base):
    __tablename__ = "beauty_saloon"
    __table_args__ = {"schema": "public"}
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(length=50), nullable=False, comment="Название салона")
    number: Mapped[str] = mapped_column(comment="Номер телефона")
    address: Mapped[str] = mapped_column(String(length=200), comment="Адрес салона")
    saloon_specs: Mapped[List['SaloonSpec']] = relationship(back_populates="beauty_saloon", lazy="selectin", cascade="all, delete", passive_deletes=True, passive_updates=True)


class Specialist(Base):
    __tablename__ = "specialist"
    __table_args__ = {"schema": "public"}
    first_name: Mapped[str] = mapped_column(String(25), nullable=False, comment="Имя специалиста")
    last_name: Mapped[str] = mapped_column(String(25), nullable=False, comment="Фамилия специалиста")
    experience: Mapped[int] = mapped_column(comment="Стаж специалиста")
    saloon_specs: Mapped[List['SaloonSpec']] = relationship(back_populates="specialist", lazy="selectin", cascade="all, delete", passive_deletes=True, passive_updates=True)


class Service(Base):
    __tablename__ = "service"
    __table_args__ = {"schema": "public"}
    name: Mapped[str] = mapped_column(String(length=100), comment="Название услуги")
    saloon_spec_services: Mapped[List['SaloonSpecService']] = relationship(back_populates="service", lazy="selectin", cascade="all, delete", passive_deletes=True, passive_updates=True)


class SaloonSpec(Base):
    __tablename__ = "saloon_spec"
    __table_args__ = {"schema": "public"}
    beauty_saloon_id: Mapped[int] = mapped_column(ForeignKey(BeautySaloon.id, ondelete='CASCADE', onupdate='CASCADE'))
    specialist_id: Mapped[int] = mapped_column(ForeignKey(Specialist.id, ondelete='CASCADE', onupdate='CASCADE'))
    beauty_saloon: Mapped['BeautySaloon'] = relationship(back_populates="saloon_specs", lazy="selectin", cascade="all")
    specialist: Mapped['Specialist'] = relationship(back_populates='saloon_specs', lazy="selectin", cascade="all")
    saloon_spec_services: Mapped[List["SaloonSpecService"]] = relationship(back_populates='saloon_spec', lazy="selectin", cascade="all, delete", passive_deletes=True, passive_updates=True)


class SaloonSpecService(Base):
    __tablename__ = "saloon_spec_service"
    __table_args__ = {"schema": "public"}
    price: Mapped[decimal.Decimal("0.00")] = mapped_column(MONEY)
    service_id: Mapped[int] = mapped_column(ForeignKey(Service.id, ondelete='CASCADE', onupdate='CASCADE'), comment="Внешний ключ услуги")
    saloon_spec_id: Mapped[int] = mapped_column(ForeignKey(SaloonSpec.id, ondelete='CASCADE', onupdate='CASCADE'))
    saloon_spec: Mapped['SaloonSpec'] = relationship(back_populates='saloon_spec_services', lazy="selectin")
    service: Mapped["Service"] = relationship(back_populates="saloon_spec_services", lazy="selectin", cascade="all")
    time_slots: Mapped[List["TimeSlot"]] = relationship(back_populates="saloon_spec_service", lazy="selectin", cascade="all, delete", passive_deletes=True, passive_updates=True)


class TimeSlot(Base):
    __tablename__ = "time_slot"
    __table_args__ = {"schema": "public"}
    date_time: Mapped[datetime.datetime] = mapped_column(nullable=False)
    saloon_spec_service_id: Mapped[int] = mapped_column(ForeignKey(SaloonSpecService.id, ondelete='CASCADE', onupdate='CASCADE'))
    appointments: Mapped[List["Appointment"]] = relationship(back_populates='time_slot', lazy='selectin',
                                                             cascade="all, delete", passive_deletes=True, passive_updates=True)
    saloon_spec_service: Mapped[SaloonSpecService] = relationship(back_populates="time_slots", lazy="selectin", cascade="all")


class Appointment(Base):
    __tablename__ = "appointment"
    __table_args__ = {"schema": "public"}
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete='CASCADE', onupdate='CASCADE'), comment="Внешний ключ пользователя")
    time_slot_id: Mapped[int] = mapped_column(ForeignKey(TimeSlot.id, ondelete='CASCADE', onupdate='CASCADE'))
    user: Mapped[User] = relationship(back_populates="appointments", lazy="selectin", cascade="all")
    time_slot: Mapped[TimeSlot] = relationship(back_populates='appointments', lazy="selectin", cascade="all")
