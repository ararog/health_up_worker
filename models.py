from sqlmodel import Field, SQLModel, select
from sqlalchemy import union_all, literal_column
from sqlalchemy.orm import registry
from sqlalchemy_utils import create_materialized_view

class Office(SQLModel, table=True):
    id: str | None = Field(primary_key=True)
    name: str
    description: str
    address: str
    phone_number: str
    email: str
    website: str
    opening_hours: str
    maps_link: str
    reviews: str

class Speciality(SQLModel, table=True):
    id: str | None = Field(primary_key=True)
    name: str
    description: str
    office_id: str | None = Field(default=None, foreign_key="office.id")
    
class BaseContact(SQLModel):
    name: str
    bio: str
    phone_number: str
    email: str
    address: str

class Owner(BaseContact, table=True):
    id: str | None = Field(primary_key=True)
    office_id: str | None = Field(default=None, foreign_key="office.id")
    
class Manager(BaseContact, table=True):
    id: str | None = Field(primary_key=True)
    office_id: str | None = Field(default=None, foreign_key="office.id")

class Doctor(BaseContact, table=True):
    id: str | None = Field(primary_key=True)
    office_id: str | None = Field(default=None, foreign_key="office.id")

class Patient(BaseContact, table=True):
    id: str | None = Field(primary_key=True)
    office_id: str | None = Field(default=None, foreign_key="office.id")

class PatientExam(SQLModel, table=True):
    id: str | None = Field(primary_key=True)
    date_time: str
    name: str
    status: str
    description: str
    patient_id: str | None = Field(default=None, foreign_key="patient.id")
    doctor_id: str | None = Field(default=None, foreign_key="doctor.id")

class PatientHistory(SQLModel, table=True):
    id: str | None = Field(primary_key=True)
    date_time: str
    description: str
    patient_id: str | None = Field(default=None, foreign_key="patient.id")
    doctor_id: str | None = Field(default=None, foreign_key="doctor.id")

class Appointment(SQLModel, table=True):
    id: str | None = Field(primary_key=True)
    date: str
    time: str
    office_id: str | None = Field(default=None, foreign_key="office.id")
    patient_id: str | None = Field(default=None, foreign_key="patient.id")
    doctor_id:  str | None = Field(default=None, foreign_key="doctor.id")
    
class Product(SQLModel, table=True):
    id: str | None = Field(primary_key=True)
    name: str
    description: str
    price: float
    office_id: str | None = Field(default=None, foreign_key="office.id")

class Inventory(SQLModel, table=True):
    id: str | None = Field(primary_key=True)
    quantity: int
    product_id: str | None = Field(default=None, foreign_key="product.id")
    office_id: str | None = Field(default=None, foreign_key="office.id")    

class ChatMessage(SQLModel, table=True):
    id: str | None = Field(primary_key=True)
    phone_number: str
    role: str | None = None
    timestamp: str
    content: bytes
    office_id:  str | None = Field(default=None, foreign_key="office.id")

mapper_registry = registry()

class Contact(SQLModel):
    __tablename__ = "contact"
    id: str
    phone_number: str
    office_id: str
    kind: str
    
selectable = union_all(
        select(
            Patient.id,
            Patient.phone_number,
            Patient.office_id,
            literal_column("'patient'").label("kind")
        ),
        select(
            Doctor.id,
            Doctor.phone_number,
            Doctor.office_id,
            literal_column("'doctor'").label("kind")
        ),
        select(
            Manager.id,
            Manager.phone_number,
            Manager.office_id,
            literal_column("'manager'").label("kind")
        ),
        select(
            Owner.id,
            Owner.phone_number,
            Owner.office_id,
            literal_column("'owner'").label("kind")
        )
    )    

class _Contact(SQLModel):    
    __table__ = create_materialized_view(
        name="contact",
        selectable=selectable,
        metadata=SQLModel.metadata,
    )

mapper_registry.map_imperatively(Contact, _Contact.__table__)