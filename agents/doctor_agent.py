import datetime
import logging
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from models import (
    Appointment,
    DoctorAppointment,
    Patient,
)

from services.doctor import (
  find_doctor_by_id,
)

from services.patient import (
  find_patient_history,
)

from services.appointment import (
    find_appointment,
    delete_appointment,
    list_doctor_appointments,
)

from services.patient import (
    find_patient,
)

logger = logging.getLogger('health_up:doctor_agent')
logger.setLevel(logging.CRITICAL)

@dataclass
class DoctorDependencies:
    office_id: str
    doctor_id: str
    doctor_phone_number: str

doctor_agent = Agent('openai:gpt-4o', system_prompt="""
                Date format is: DD/MM/YYYY
                You are a doctor secretary in a dental office. Perform the following steps:
                1. Use the `get_doctor` tool to retrieve doctor info from database.
                2. When greeting doctor, please greet doctor by his name. How can I help you? Show a list of available commands:
                    1. List appointments
                3. Use the `list_appointments` tool to get a list of doctor existing appointments.
                4. If doctor says he wants to see his appointments, show numbered list of doctor appointments in the following format: <time> - <patient_name>
                5. Ask the doctor to select a appointment by number.
                6. If doctor choose an appointment, extract patient id.
                7. Ask doctor if he wants to see patient history.
                8. If yes, use the `get_patient_history` tool to retrieve patient history from database.
                9. Show list of patient history in the following format:
                    - Patient: <patient_name>
                    - Date: <date_time>
                    - Description: <description>
              """)

@doctor_agent.system_prompt
def add_date_time() -> str:
    logger.info("Add date and time...")
    return f"Current date and time is: {datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")}"
  
@doctor_agent.tool
def list_appointments(ctx: RunContext[DoctorDependencies]) -> list[DoctorAppointment]:
    logger.info("Listing appointments...")
    return list_doctor_appointments(ctx.deps.doctor_id)

@doctor_agent.tool
def get_doctor(ctx: RunContext[DoctorDependencies]) -> Patient:
    logger.info("Get doctor...")
    return find_doctor_by_id(
      ctx.deps.doctor_id, 
    )
    
    
@doctor_agent.tool_plain
def get_patient_history(patient_id) -> Patient:
    logger.info("Get patient history...")
    return find_patient_history(
      patient_id
    )
  
@doctor_agent.tool_plain
def cancel_appointment(appointment: Appointment) -> bool:
    logger.info("Canceling appointment: ", appointment)
    return delete_appointment(appointment)
