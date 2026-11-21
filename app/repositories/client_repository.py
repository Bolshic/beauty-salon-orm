from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.client import Client


class ClientRepository:
    """Репозиторий для работы с клиентами салона.

    commit() здесь не вызывается, транзакцией управляет код, который
    создал сессию. Так несколько операций можно сохранить разом.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    # Create
    def add(self, client: Client) -> Client:
        self.session.add(client)
        self.session.flush()  # чтобы сразу получить id
        return client

    # Read
    def get_by_id(self, client_id: int) -> Optional[Client]:
        return self.session.get(Client, client_id)

    def get_by_phone(self, phone: str) -> Optional[Client]:
        stmt = select(Client).where(Client.phone == phone)
        return self.session.scalars(stmt).one_or_none()

    def get_all(self) -> List[Client]:
        stmt = select(Client).order_by(Client.full_name)
        return list(self.session.scalars(stmt))

    def search_by_name(self, text: str) -> List[Client]:
        stmt = select(Client).where(Client.full_name.contains(text)).order_by(Client.full_name)
        return list(self.session.scalars(stmt))

    def get_with_appointments(self, client_id: int) -> Optional[Client]:
        # записи клиента подгружаются сразу, без лишних запросов (N+1)
        stmt = (
            select(Client)
            .where(Client.id == client_id)
            .options(selectinload(Client.appointments))
        )
        return self.session.scalars(stmt).one_or_none()

    # Update
    def update(self, client_id: int, **fields) -> Optional[Client]:
        client = self.get_by_id(client_id)
        if client is None:
            return None
        for name, value in fields.items():
            setattr(client, name, value)
        return client

    # Delete
    def delete(self, client_id: int) -> bool:
        client = self.get_by_id(client_id)
        if client is None:
            return False
        self.session.delete(client)
        return True
