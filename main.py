import json
import openai
import logging
from uuid_extensions import uuid7str
from dataclasses import dataclass
from kafka import KafkaConsumer
from decouple import config
from twilio.rest import Client
from pydantic_ai import Agent, RunContext
from sqlmodel import select
from services.media import transcribe_media
from services.messaging import send_reply
from services.database import (
    Appointment,
    ChatMessage,
    Patient,
    find_patient_by_phone_number,
    find_appointment_by_phone_number,
    add_patient,
    add_appointment,
    create_db_and_tables,
    add_message_to_conversation,
    get_conversation_messages,
)
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)

logger = logging.getLogger('kafka')
logger.setLevel(logging.CRITICAL)

account_sid = config("TWILIO_ACCOUNT_SID")
auth_token = config("TWILIO_AUTH_TOKEN")

twilio_client = Client(account_sid, auth_token)
openai_client = openai.OpenAI(api_key=config("OPENAI_API_KEY"))

@dataclass
class SupportDependencies:
  phone_number: str

agent = Agent('openai:gpt-4o', system_prompt="""
                You are a secretary in a dental office. Perform the following steps:
                1. When greeting the patient, use the `get_patient` tool to retrieve the patient from the database.
                2. Use `get_appointment` to verify for an existing appointment.
                3. If there is an existing appointment, say: Hello, welcome back. You are an scheduled appointment, do you want to reschedule or cancel the appointment?
                4. If there is no existing appointment, say: Hello, welcome to the office. How may I help you today?
                5. If the patient says they want to make an appointment and you don't know their name, ask for their name.
                6. If the patient gives their name, use the `create_patient` tool to create a new patient.
                7. Ask for the day and time they want to make the appointment.
                8. If the patient gives the date and time of the appointment, repeat the date and time the patient gave and ask the patient to confirm.
                9. If the patient confirms, extract appointment.
                10. Use the `create_appointment` tool to schedule the appointment.
                11. End the appointment by saying: Goodbye!
              """)

@agent.tool
def get_patient(ctx: RunContext[SupportDependencies]) -> Patient:
    return find_patient_by_phone_number(ctx.deps.phone_number)

@agent.tool
def get_appointment(ctx: RunContext[SupportDependencies]) -> Appointment:
    return find_appointment_by_phone_number(ctx.deps.phone_number)
  
@agent.tool
def create_patient(ctx: RunContext[SupportDependencies], 
                   patient: Patient) -> Patient:
    patient.id = uuid7str()
    patient.phone_number = ctx.deps.phone_number
    add_patient(patient)
    return patient

@agent.tool
def create_appointment(ctx: RunContext[SupportDependencies], 
                       appointment: Appointment) -> Appointment:
    appointment.id = uuid7str()
    add_appointment(appointment, ctx.deps.phone_number)
    return appointment

def to_chat_message(m: ModelMessage) -> ChatMessage:
    first_part = m.parts[0]
    if isinstance(m, ModelRequest):
        if isinstance(first_part, UserPromptPart):
            assert isinstance(first_part.content, str)
            return {
                'role': 'user',
                'timestamp': first_part.timestamp.isoformat(),
                'content': first_part.content,
            }
    elif isinstance(m, ModelResponse):
        if isinstance(first_part, TextPart):
            return {
                'role': 'model',
                'timestamp': m.timestamp.isoformat(),
                'content': first_part.content,
            }
    raise UnexpectedModelBehavior(f'Unexpected message type for chat app: {m}')

def handle_message(message):
  content = message["body"]
  num_media = int(message["num_media"] or 0)
  if num_media > 0:
      media_url = message["media_url"]
      mime_type = message["media_type"]
      content = transcribe_media(media_url, mime_type, twilio_client, openai_client)
  
  parsed_number = message["from_number"].split(':')[1]
  
  deps = SupportDependencies(phone_number=parsed_number)
  
  messages = get_conversation_messages(parsed_number)
  response = agent.run_sync(content, message_history=messages, deps=deps)
  ai_message = add_message_to_conversation(
    parsed_number, response.new_messages_json())

  print(f"Response: {response.data}")
    
  # send_reply(message["from_number"], 
  #            response.data, 
  #            num_media > 0, 
  #            ai_message.id, 
  #            twilio_client, 
  #            openai_client)


def main():
  kafka_broker = config('KAFKA_BROKER')
  consumer = KafkaConsumer(
    'process_message', 
    bootstrap_servers=kafka_broker, 
    group_id='health_up',
    value_deserializer=lambda m: json.loads(m.decode('ascii')))
  for msg in consumer:
    handle_message(msg.value)

if __name__ == "__main__":
  create_db_and_tables()
  main()
