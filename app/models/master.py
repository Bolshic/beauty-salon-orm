from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Master(Base):
    """Мастер салона: парикмахер, мастер маникюра и т.д."""
    __tablename__ = "masters"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150))
    specialization: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20))

    appointments: Mapped[List["Appointment"]] = relationship(back_populates="master")

    def __repr__(self) -> str:
        return f"<Master id={self.id} name={self.full_name!r} spec={self.specialization!r}>"
