import datetime
from uuid_extensions import uuid7str
from database import engine
from sqlmodel import (
    select,
    Session
)
from models import (
    Appointment, 
    Office, 
    Patient
)
    
def list_existing_appointments(office_id) -> list[Appointment]:
    with Session(engine) as session:
        actual_date_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
        statement = select(Appointment)
        statement = statement.where(Appointment.date >= actual_date_time)
        statement = statement.where(Appointment.office_id == office_id)
        statement = statement.limit(10)
        results = session.exec(statement)
        
        appointments: list[Appointment] = []
        for appointment in results:
            appointments.extend(appointment)

        return appointments
    
def find_appointment(office_id, phone_number) -> Patient: 
    with Session(engine) as session:
        actual_date_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
        statement = select(Appointment, Patient, Office)
        statement = statement.where(Appointment.office_id == office_id)
        statement = statement.where(Appointment.patient_id == Patient.id)
        statement = statement.where(Appointment.date > actual_date_time)
        statement = statement.where(Patient.phone_number == phone_number)
        results = session.exec(statement)
        
        next_appointment = results.first()
        if next_appointment:
            return next_appointment[0]
        return None
          
def add_appointment(appointment, phone_number) -> Appointment: 
    with Session(engine) as session:
        statement = select(Patient)
        statement = statement.where(Patient.phone_number == phone_number)
        results = session.exec(statement)
        patient = results.one_or_none()
        if patient:
            appointment.patient_id = patient.id

        session.add(appointment)
        session.commit()
        return appointment

def delete_appointment(appointment: Appointment) -> bool: 
    with Session(engine) as session:
        statement = select(Appointment).where(Appointment.id == appointment.id)
        results = session.exec(statement)
        appointment = results.one()
        session.delete(appointment)
        session.commit()
        return True

