from database import engine
from sqlmodel import (
    select,
    Session
)
from models import (
    Patient,
    PatientHistory
)
    
def add_patient(patient) -> Patient: 
    with Session(engine) as session:
        session.add(patient)
        session.commit()
        return patient

def find_patient(office_id, patient_id) -> Patient: 
    with Session(engine) as session:
        statement = select(Patient)
        statement = statement.where(Patient.office_id == office_id)
        statement = statement.where(Patient.id == patient_id)
        results = session.exec(statement)
        return results.first()

def find_patient_history(patient_id) -> Patient: 
    with Session(engine) as session:
        statement = select(PatientHistory)
        statement = statement.where(PatientHistory.patient_id == patient_id)
        statement = statement.limit(5)
        statement = statement.order_by(PatientHistory.date_time.desc())
        results = session.exec(statement)
        return results.first()