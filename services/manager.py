from database import engine
from sqlmodel import Session, select

from models import (
    Manager, 
)

def find_manager_by_id(manager_id: str) -> Manager:
    with Session(engine) as session:
        statement = select(Manager)
        statement = statement.where(Manager.id == manager_id)
        results = session.exec(statement)
        return results.first()

def find_manager_by_phone_number(office_id, phone_number) -> Manager:
    with Session(engine) as session:
        statement = select(Manager)
        statement = statement.where(Manager.office_id == office_id)
        statement = statement.where(Manager.phone_number == phone_number)
        results = session.exec(statement)
        return results.first()