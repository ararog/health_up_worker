import datetime
import pytz
from database import engine
from sqlmodel import (
    select,
    Session
)
from models import (
    Appointment, 
    DoctorAppointment,
    Office, 
    Patient
)
    
def list_office_appointments(office_id, actual_date, actual_time) -> list[Appointment]:
    with Session(engine) as session:
        statement = select(Appointment)
        statement = statement.where(Appointment.date >= actual_date)
        statement = statement.where(Appointment.time >= actual_time)
        statement = statement.where(Appointment.office_id == office_id)
        statement = statement.limit(10)
        results = session.exec(statement)
        
        appointments: list[Appointment] = []
        for appointment in results:
            appointments.extend(appointment)

        return appointments

def list_doctor_appointments(doctor_id, actual_date, actual_time) -> list[DoctorAppointment]:
    with Session(engine) as session:
        statement = select(Appointment, Patient).join(Patient)
        statement = statement.where(Appointment.date >= actual_date)
        statement = statement.where(Appointment.time >= actual_time)
        statement = statement.where(Appointment.doctor_id == doctor_id)
        results = session.exec(statement)
        
        appointments: list[DoctorAppointment] = []
        for appointment, patient in results:
            appointments.extend(
              DoctorAppointment(
                patient_id=patient.id, 
                patient_name=patient.name, 
                date=appointment.date, 
                time=appointment.time
              )
            )

        return appointments
    
def find_appointment(office_id, patient_id, actual_date, actual_time) -> Patient: 
    with Session(engine) as session:
        actual_date_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
        statement = select(Appointment, Patient, Office)
        statement = statement.where(Appointment.office_id == office_id)
        statement = statement.where(Appointment.patient_id == Patient.id)
        statement = statement.where(Appointment.date >= actual_date)
        statement = statement.where(Appointment.time >= actual_time)
        statement = statement.where(Patient.id == patient_id)
        results = session.exec(statement)
        
        next_appointment = results.first()
        if next_appointment:
            return next_appointment[0]
        return None
          
def add_appointment(appointment) -> Appointment: 
    with Session(engine) as session:
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

