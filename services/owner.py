from database import engine
from sqlmodel import Session, select

from models import (
    Owner, 
)

def find_owner_by_id(owner_id: str) -> Owner:
    with Session(engine) as session:
        statement = select(Owner)
        statement = statement.where(Owner.id == owner_id)
        results = session.exec(statement)
        return results.first()

def find_owner_by_phone_number(office_id, phone_number) -> Owner:
    with Session(engine) as session:
        statement = select(Owner)
        statement = statement.where(Owner.office_id == office_id)
        statement = statement.where(Owner.phone_number == phone_number)
        results = session.exec(statement)
        return results.first()