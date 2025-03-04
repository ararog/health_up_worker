import datetime
from uuid_extensions import uuid7str
from decouple import config
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
)

database_url = config("DATABASE_URL")

engine = create_engine(database_url)  

class Patient(SQLModel, table=True):
    id: str | None = Field(primary_key=True)
    name: str
    phone_number: str | None = None

class Appointment(SQLModel, table=True):
    id: str | None = Field(primary_key=True)
    date: str
    time: str
    patient_id: str | None = Field(default=None, foreign_key="patient.id")
    
class ChatMessage(SQLModel, table=True):
    id: str | None = Field(primary_key=True)
    phone_number: str
    role: str | None = None
    timestamp: str
    content: bytes
    
def find_patient_by_phone_number(phone_number) -> Patient: 
    with Session(engine) as session:
        statement = select(Patient)
        statement = statement.where(Patient.phone_number == phone_number)
        results = session.exec(statement)
        return results.one_or_none()

def find_appointment_by_phone_number(phone_number) -> Patient: 
    with Session(engine) as session:
        actual_date_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
        statement = select(Appointment, Patient)
        statement = statement.where(Appointment.patient_id == Patient.id)
        statement = statement.where(Patient.phone_number == phone_number)
        statement = statement.where(Appointment.date > actual_date_time)
        results = session.exec(statement)
        return results.one_or_none()
    
def add_patient(patient) -> Patient: 
    with Session(engine) as session:
        session.add(patient)
        session.commit()
        return patient
      
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

def get_conversation_messages(from_number: str) -> list[ModelMessage]:
    with Session(engine) as session:
        messages: list[ModelMessage] = []
        statement = select(ChatMessage)
        statement = statement.where(ChatMessage.phone_number == from_number)
        statement = statement.limit(1)
        statement = statement.order_by(ChatMessage.timestamp.asc())
        results = session.exec(statement)
        for message in results:
            messages.extend(ModelMessagesTypeAdapter.validate_json(message.content))

        actual_date_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
        statement = select(ChatMessage)
        statement = statement.where(ChatMessage.phone_number == from_number)
        statement = statement.where(ChatMessage.timestamp < actual_date_time)
        statement = statement.limit(10)
        statement = statement.order_by(ChatMessage.timestamp.asc())
        results = session.exec(statement)
        
        for message in results:
            messages.extend(ModelMessagesTypeAdapter.validate_json(message.content))
        return messages
      
def add_message_to_conversation(from_number: str, content: str):
    with Session(engine) as session:  
      message = ChatMessage(
        id=uuid7str(),
        phone_number=from_number, 
        timestamp=datetime.datetime.now().isoformat(), 
        content=content)
      session.add(message)
      session.commit()
      return message

def create_db_and_tables():  
    SQLModel.metadata.create_all(engine) 
