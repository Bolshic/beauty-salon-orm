# все модели импортируются здесь, чтобы alembic видел их при --autogenerate
from app.models.client import Client
from app.models.master import Master
from app.models.service import Service
from app.models.appointment import Appointment

__all__ = ["Client", "Master", "Service", "Appointment"]
