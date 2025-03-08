from database import engine
from sqlmodel import (
    select,
    Session
)
from models import (
    Office, 
)

def find_office_by_phone_number(phone_number) -> Office: 
    with Session(engine) as session:
        statement = select(Office)
        statement = statement.where(Office.phone_number == phone_number)
        results = session.exec(statement)
        return results.first()  
    
def find_office_by_id(office_id) -> Office: 
    with Session(engine) as session:
        statement = select(Office)
        statement = statement.where(Office.id == office_id)
        results = session.exec(statement)
        return results.first()    
