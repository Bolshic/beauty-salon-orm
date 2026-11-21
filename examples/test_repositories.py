"""Проверка репозиториев на базе salon.db.

Перед запуском базу нужно создать миграцией: alembic upgrade head
Запуск: python -m examples.test_repositories
"""
from datetime import datetime, timedelta

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Appointment, Client, Master, Service
from app.repositories import AppointmentRepository, ClientRepository


class RepositoryTest:

    def __init__(self):
        self.session = SessionLocal()
        self.clients = ClientRepository(self.session)
        self.appointments = AppointmentRepository(self.session)

    def prepare(self):
        """Мастер и услуга, если их ещё нет в базе."""
        self.master = self.session.scalars(select(Master)).first()
        if self.master is None:
            self.master = Master(full_name="Смирнова Ольга", specialization="парикмахер", phone="+79001112233")
            self.session.add(self.master)
        self.service = self.session.scalars(select(Service).where(Service.title == "Стрижка женская")).first()
        if self.service is None:
            self.service = Service(title="Стрижка женская", price=1500, duration_min=60)
            self.session.add(self.service)
        self.session.commit()

    def test_create(self):
        print("\n--- Создание клиентов ---")
        for name, phone in [("Иванова Мария", "+79101234567"),
                            ("Петрова Анна", "+79107654321"),
                            ("Козлова Елена", "+79105556677")]:
            client = self.clients.get_by_phone(phone)
            if client is None:
                client = self.clients.add(Client(full_name=name, phone=phone))
            print("добавлен:", client)
        self.session.commit()

    def test_read(self):
        print("\n--- Чтение ---")
        print("все клиенты:", self.clients.get_all())
        print("по телефону:", self.clients.get_by_phone("+79107654321"))
        print("поиск 'ова':", self.clients.search_by_name("ова"))

    def test_update(self):
        print("\n--- Изменение ---")
        client = self.clients.get_by_phone("+79101234567")
        self.clients.update(client.id, email="maria@mail.ru")
        self.session.commit()
        print("email изменён:", client.full_name, client.email)

    def test_appointments(self):
        print("\n--- Онлайн-запись ---")
        client = self.clients.get_by_phone("+79107654321")
        start = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=1)
        if self.appointments.is_master_free(self.master.id, start, self.service):
            self.appointments.add(Appointment(client_id=client.id, master_id=self.master.id,
                                              service_id=self.service.id, start_time=start))
            self.session.commit()
            print("запись создана на", start.strftime("%d.%m.%Y %H:%M"))
        print("мастер свободен в 12:30?",
              self.appointments.is_master_free(self.master.id, start + timedelta(minutes=30), self.service))
        print("мастер свободен в 13:00?",
              self.appointments.is_master_free(self.master.id, start + timedelta(hours=1), self.service))
        print("расписание мастера:", self.appointments.get_by_master_on_day(self.master.id, start.date()))
        print("записи клиента:", self.clients.get_with_appointments(client.id).appointments)

    def test_delete(self):
        print("\n--- Удаление ---")
        client = self.clients.get_by_phone("+79105556677")
        print("удалён:", self.clients.delete(client.id))
        self.session.commit()
        print("осталось клиентов:", len(self.clients.get_all()))

    def run(self):
        self.prepare()
        self.test_create()
        self.test_read()
        self.test_update()
        self.test_appointments()
        self.test_delete()
        self.session.close()


if __name__ == "__main__":
    RepositoryTest().run()
