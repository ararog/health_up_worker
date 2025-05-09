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

from utils import actual_date_time
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
    
# ollama_model = OpenAIModel(
#     model_name='phi4-mini', provider=OpenAIProvider(base_url='http://localhost:11434/v1')
# )    

appointment_agent = Agent("openai:gpt-4o", system_prompt="""
                Date format is: DD/MM/YYYY
                Reply patient with patient name
                You are a secretary in a dental office. Perform the following steps:
                1. Say patient can use word 'menu' to see the menu.
                2. Use `get_office_info` tool to retrieve office info from database.
                3. Use `get_patient` tool to retrieve patient from database.
                4. Use `get_appointment` tool to retrieve existing appointment from database. 
                5. Use `list_specialties` tool to retrieve specialties from database.
                6. Use `list_doctors` tool to retrieve doctors from database.
                7. Use `cancel_appointment` tool to cancel an appointment.
                8. Use `current_date_time` tool to get current date time.
                9. When greeting the patient, greet patient with his name.
                10. If there is an existing appointment, say: Hello, welcome back. You have an scheduled existing appointment. What do you want? Show a list of available menu options:
                    1. Cancel appointment
                    2. Reschedule appointment                
                11. If there is no existing appointment, say: Hello, welcome to the office. How may I help you today? Show a list of available menu options:
                    1. Make appointment
                    2. Business hours
                    3. Office location
                    4. Specialties
                12. If the patient says they want to make an appointment and you don't know their name, ask for their name.
                13. If the patient gives their name, use the `create_patient` tool to create a new patient.
                14. Show numbered list of doctors by name.
                15. Ask the patient to select a doctor by number.
                16. If patient choose a doctor, extract doctor id.
                17. Use the `list_appointments` tool to get a list of office existing appointments.
                18. Based on a list of existing appointments, suggest a numbered list of 10 available dates and hours for the next two weeks to the patient using current date and time.
                19. Ask the patient to select a date and time by number.
                20. Use patient id and doctor id to schedule the appointment.
                21. If the patient confirms, extract appointment.
                22. Use the `create_appointment` tool to schedule the appointment.
                23. Ask if user knows office location, give two options:
                    1. Yes
                    2. No
                24. If the patient says no, give the office location.
                25. If the patient says yes, say: Ok, see you soon!
              """)

@appointment_agent.tool
def current_date_time(ctx: RunContext[AppointmentDependencies]) -> str:
    logger.info("Add date and time...")
    now = actual_date_time('America/Sao_Paulo')
    return f"Current date and time is: {now.date_time}"

@appointment_agent.tool
def get_patient_id(ctx: RunContext[AppointmentDependencies]) -> Patient:
    return ctx.deps.patient_id

@appointment_agent.tool
def get_patient(ctx: RunContext[AppointmentDependencies]) -> Patient:
    logger.info("Get patient...")
    patient = find_patient(ctx.deps.office_id, ctx.deps.patient_phone_number)
    return patient

@appointment_agent.tool
def create_patient(ctx: RunContext[AppointmentDependencies], 
                   patient: Patient) -> Patient:
    patient.id = uuid7str()
    patient.phone_number = ctx.deps.patient_phone_number
    patient.office_id = ctx.deps.office_id
    add_patient(patient)
    return patient

@appointment_agent.tool
def get_office_info(ctx: RunContext[AppointmentDependencies]) -> Office:
    logger.info("Get office info...")
    return find_office_by_id(ctx.deps.office_id)

@appointment_agent.tool
def list_doctors(ctx: RunContext[AppointmentDependencies]) -> list[Doctor]:
    logger.info("Get office doctors...")
    return find_doctors_by_office_id(ctx.deps.office_id)

@appointment_agent.tool
def get_doctor(ctx: RunContext[AppointmentDependencies], doctor_name: str) -> Patient:
    logger.info("Get doctor...")
    return find_doctor_by_name(
      ctx.deps.office_id, 
      doctor_name
    )
    
@appointment_agent.tool
def list_specialities(ctx: RunContext[AppointmentDependencies]) -> list[Speciality]:
    logger.info("Get office specialists...")
    return find_specilities_by_office_id(ctx.deps.office_id)
  
@appointment_agent.tool
def list_appointments(ctx: RunContext[AppointmentDependencies]) -> list[Appointment]:
    logger.info("Listing appointments...")
    now = actual_date_time('America/Sao_Paulo')
    return list_office_appointments(ctx.deps.office_id, now.date_time)
  
@appointment_agent.tool
def get_appointment(ctx: RunContext[AppointmentDependencies]) -> Appointment:
    logger.info("Get appointment...")
    now = actual_date_time('America/Sao_Paulo')
    return find_appointment(ctx.deps.office_id, 
                            ctx.deps.patient_id, 
                            now.date_time)

@appointment_agent.tool_plain
def cancel_appointment(appointment: Appointment) -> bool:
    logger.info("Canceling appointment: ", appointment)
    return delete_appointment(appointment)
  
@appointment_agent.tool
def create_appointment(ctx: RunContext[AppointmentDependencies], 
                       appointment: Appointment, patient_id, doctor_id) -> Appointment:
    logger.info("Creating appointment: ", appointment)
    appointment.id = uuid7str()
    appointment.office_id = ctx.deps.office_id
    appointment.doctor_id = doctor_id
    appointment.patient_id = patient_id if patient_id else ctx.deps.patient_id
    add_appointment(appointment)
    return appointment