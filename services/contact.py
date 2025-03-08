from database import engine
from sqlmodel import (
    select,
    Session
)
from models import (
    Contact, 
)

def find_contact_by_phone_number(office_id: str, phone_number: str) -> Contact | None:
    with Session(engine) as session:
        statement = select(Contact)
        statement = statement.where(Contact.office_id == office_id)
        statement = statement.where(Contact.phone_number == phone_number)
        contact = session.exec(statement).first()
        return contact