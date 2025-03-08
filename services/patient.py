from database import engine
from sqlmodel import (
    select,
    Session
)
from models import (
    Patient
)
    
def add_patient(patient) -> Patient: 
    with Session(engine) as session:
        session.add(patient)
        session.commit()
        return patient

def find_patient(office_id, phone_number) -> Patient: 
    with Session(engine) as session:
        statement = select(Patient)
        statement = statement.where(Patient.office_id == office_id)
        statement = statement.where(Patient.phone_number == phone_number)
        results = session.exec(statement)
        return results.first()
