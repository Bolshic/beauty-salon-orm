from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Service(Base):
    """Услуга салона"""
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True)
    price: Mapped[int]          # цена в рублях
    duration_min: Mapped[int]   # длительность в минутах

    appointments: Mapped[List["Appointment"]] = relationship(back_populates="service")

    def __repr__(self) -> str:
        return f"<Service id={self.id} title={self.title!r} price={self.price}>"
