from datetime import date, datetime, time, timedelta
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.appointment import Appointment
from app.models.service import Service


class AppointmentRepository:
    """Репозиторий записей клиентов (основа онлайн-записи)."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, appointment: Appointment) -> Appointment:
        self.session.add(appointment)
        self.session.flush()
        return appointment

    def get_by_id(self, appointment_id: int) -> Optional[Appointment]:
        return self.session.get(Appointment, appointment_id)

    def get_by_client(self, client_id: int) -> List[Appointment]:
        stmt = (
            select(Appointment)
            .where(Appointment.client_id == client_id)
            .order_by(Appointment.start_time)
        )
        return list(self.session.scalars(stmt))

    def get_by_master_on_day(self, master_id: int, day: date) -> List[Appointment]:
        # расписание мастера на день, вместе с услугой и клиентом
        start = datetime.combine(day, time.min)
        end = start + timedelta(days=1)
        stmt = (
            select(Appointment)
            .where(
                Appointment.master_id == master_id,
                Appointment.start_time >= start,
                Appointment.start_time < end,
                Appointment.status != "отменена",
            )
            .options(joinedload(Appointment.service), joinedload(Appointment.client))
            .order_by(Appointment.start_time)
        )
        return list(self.session.scalars(stmt))

    def is_master_free(self, master_id: int, start_time: datetime, service: Service) -> bool:
        """Свободен ли мастер на время услуги (записи не должны пересекаться)."""
        end_time = start_time + timedelta(minutes=service.duration_min)
        for a in self.get_by_master_on_day(master_id, start_time.date()):
            a_end = a.start_time + timedelta(minutes=a.service.duration_min)
            if a.start_time < end_time and start_time < a_end:
                return False
        return True

    def cancel(self, appointment_id: int) -> bool:
        appointment = self.get_by_id(appointment_id)
        if appointment is None:
            return False
        appointment.status = "отменена"
        return True

    def delete(self, appointment_id: int) -> bool:
        appointment = self.get_by_id(appointment_id)
        if appointment is None:
            return False
        self.session.delete(appointment)
        return True
