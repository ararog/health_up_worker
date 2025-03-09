import datetime
import logging
from dataclasses import dataclass
from uuid_extensions import uuid7str
from pydantic_ai import Agent, RunContext
from models import (
    Office,
    Appointment,
    Patient,
    Doctor,
    Speciality,
)

from services.speciality import find_specilities_by_office_id
from services.doctor import (
  find_doctor_by_name,
  find_doctors_by_office_id
)

from services.office import (
  find_office_by_id,
)

from services.appointment import (
    list_office_appointments,
    find_appointment,
    add_appointment,
    delete_appointment
)

from services.patient import (
    find_patient,
    add_patient,
)

logger = logging.getLogger('health_up:appointment_agent')
logger.setLevel(logging.CRITICAL)

@dataclass
class AppointmentDependencies:
    office_id: str
    patient_id: str
    patient_phone_number: str

appointment_agent = Agent('openai:gpt-4o', system_prompt="""
                You are a secretary in a dental office. Perform the following steps:
                1. Use the `get_office_info` tool to retrieve office info from database.
                2. Use the `list_specialties` tool to retrieve specialties from database.
                3. Use the `list_doctors` tool to retrieve doctors from database.
                4. Use the `cancel_appointment` tool to cancel an appointment.
                4. When greeting the patient, use the `get_patient` tool to retrieve patient from database.
                5. When greeting the patient, use the `get_appointment` tool to retrieve existing appointment from database. 
                6. If there is an existing appointment, say: Hello, welcome back. You have an scheduled existing appointment, do you want to reschedule or cancel the appointment?
                7. If there is no existing appointment, say: Hello, welcome to the office. How may I help you today?
                8. If the patient says they want to make an appointment and you don't know their name, ask for their name.
                9. If the patient gives their name, use the `create_patient` tool to create a new patient.
                10. Show numbered list of doctors by name.
                11. Ask the patient to select a doctor by number.
                12. If patient choose a doctor, extract doctor id.
                13. Use the `list_appointments` tool to get a list of office existing appointments.
                14. Based on a list of existing appointments, suggest a numbered list of 10 available dates and hours for the next two weeks to the patient.
                15. Ask the patient to select a date and time by number.
                16. If the patient confirms, extract appointment.
                17. Use the `create_appointment` tool to schedule the appointment.
                18. End the appointment by saying: See you soon!
              """)

@appointment_agent.system_prompt
def add_date_time() -> str:
    logger.info("Add date and time...")
    return f"Current date and time is: {datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")}"

@appointment_agent.tool
def get_office_info(ctx: RunContext[AppointmentDependencies]) -> Office:
    logger.info("Get office info...")
    return find_office_by_id(ctx.deps.office_id)

@appointment_agent.tool
def list_doctors(ctx: RunContext[AppointmentDependencies]) -> list[Doctor]:
    logger.info("Get office doctors...")
    return find_doctors_by_office_id(ctx.deps.office_id)

@appointment_agent.tool
def list_specialities(ctx: RunContext[AppointmentDependencies]) -> list[Speciality]:
    logger.info("Get office specialists...")
    return find_specilities_by_office_id(ctx.deps.office_id)
  
@appointment_agent.tool
def list_appointments(ctx: RunContext[AppointmentDependencies]) -> list[Appointment]:
    logger.info("Listing appointments...")
    return list_office_appointments(ctx.deps.office_id)

@appointment_agent.tool
def get_doctor(ctx: RunContext[AppointmentDependencies], doctor_name: str) -> Patient:
    logger.info("Get doctor...")
    return find_doctor_by_name(
      ctx.deps.office_id, 
      doctor_name
    )

@appointment_agent.tool
def get_patient(ctx: RunContext[AppointmentDependencies]) -> Patient:
    logger.info("Get patient...")
    patient = find_patient(ctx.deps.office_id, ctx.deps.patient_id)
    return patient

@appointment_agent.tool
def get_appointment(ctx: RunContext[AppointmentDependencies]) -> Appointment:
    logger.info("Get appointment...")
    return find_appointment(
      ctx.deps.office_id, 
      ctx.deps.patient_id
    )
  
@appointment_agent.tool
def create_patient(ctx: RunContext[AppointmentDependencies], 
                   patient: Patient) -> Patient:
    patient.id = uuid7str()
    patient.phone_number = ctx.deps.patient_phone_number
    patient.office_id = ctx.deps.office_id
    add_patient(patient)
    return patient

@appointment_agent.tool_plain
def cancel_appointment(appointment: Appointment) -> bool:
    logger.info("Canceling appointment: ", appointment)
    return delete_appointment(appointment)
  
@appointment_agent.tool
def create_appointment(ctx: RunContext[AppointmentDependencies], 
                       appointment: Appointment, 
                       patient: Patient,
                       doctor_id) -> Appointment:
    logger.info("Creating appointment: ", appointment)
    appointment.id = uuid7str()
    appointment.office_id = ctx.deps.office_id
    appointment.doctor_id = doctor_id
    appointment.patient_id = patient.id
    add_appointment(appointment)
    return appointment