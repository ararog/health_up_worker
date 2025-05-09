from database import engine
from sqlmodel import (
    select,
    Session
)
from models import (
    Doctor, 
)

def find_doctor_by_id(doctor_id: str) -> Doctor:
    with Session(engine) as session:
        statement = select(Doctor)
        statement = statement.where(Doctor.id == doctor_id)
        results = session.exec(statement)
        return results.first()

def find_doctor_by_phone_number(office_id, phone_number) -> Doctor:
    with Session(engine) as session:
        statement = select(Doctor)
        statement = statement.where(Doctor.office_id == office_id)
        statement = statement.where(Doctor.phone_number == phone_number)
        results = session.exec(statement)
        return results.first()
      
def find_doctor_by_name(office_id, doctor_name) -> Doctor:
    with Session(engine) as session:
        statement = select(Doctor)
        statement = statement.where(Doctor.office_id == office_id)
        statement = statement.where(Doctor.name == doctor_name)
        results = session.exec(statement)
        return results.first()
    
def find_doctors_by_office_id(office_id) -> list[Doctor]: 
    with Session(engine) as session:
        statement = select(Doctor)
        statement = statement.where(Doctor.office_id == office_id)
        results = session.exec(statement)
        
        doctors: list[Doctor] = []
        for doctor in results:
            doctors.extend(doctor)
                    
        return doctors     
