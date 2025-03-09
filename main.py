import os
import json
import openai
import logging
from kafka import KafkaConsumer
from dotenv import load_dotenv
from twilio.rest import Client
from services.media import transcribe_media
from services.messaging import send_reply
from services.contact import find_contact_by_phone_number

from agents.appointment_agent import (
  appointment_agent,
  AppointmentDependencies
)

from agents.doctor_agent import (
  doctor_agent,
  DoctorDependencies
)

from agents.manager_agent import (
  manager_agent,
  ManagerDependencies
)

from agents.owner_agent import (
  owner_agent,
  OwnerDependencies
)

from models import (
    ChatMessage,
)

from services.office import (
  find_office_by_phone_number
)

from services.chat import (
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

load_dotenv()

logger = logging.getLogger('kafka')
logger.setLevel(logging.INFO)

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

twilio_client = Client(account_sid, auth_token)
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
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
  media_path = os.getenv("MEDIA_PATH")
  if num_media > 0:
      media_url = message["media_url"]
      mime_type = message["media_type"]
      content = transcribe_media(media_url, media_path, mime_type, twilio_client, openai_client)
  
  office_phone_number = message["to_number"]
  if ':' in office_phone_number:
      office_phone_number = office_phone_number.split(':')[1]
  else:
      return
  contact_phone_number = message["from_number"]
  if ':' in contact_phone_number:
      contact_phone_number = contact_phone_number.split(':')[1]
  else:
      return
  
  office = find_office_by_phone_number(office_phone_number)
  contact = find_contact_by_phone_number(office.id, contact_phone_number)
  
  print(f"Received contact: {contact}")
  
  response = None
  messages = get_conversation_messages(office.id, contact_phone_number)
  if contact is None or contact.kind == 'patient':        
    deps = AppointmentDependencies(
      office_id=office.id, 
      patient_id = None if contact is None else contact.id,
      patient_phone_number=contact_phone_number)    
    response = appointment_agent.run_sync(content, 
      message_history=messages, 
      deps=deps)
  elif contact.kind == 'doctor':
    deps = DoctorDependencies(
      office_id=office.id, 
      doctor_id=contact.id, 
      doctor_phone_number=contact_phone_number)
    response = doctor_agent.run_sync(
      content, 
      message_history=messages, 
      deps=deps)
  elif contact.kind == 'manager':
    deps = ManagerDependencies(
      office_id=office.id, 
      manager_id=contact.id, 
      manager_phone_number=contact_phone_number)
    response = manager_agent.run_sync(
      content, 
      message_history=messages, 
      deps=deps)
  elif contact.kind == 'owner':
    deps = OwnerDependencies(
      office_id=office.id, 
      owner_id=contact.id, 
      owner_phone_number=contact_phone_number)
    response = owner_agent.run_sync(
      content, 
      message_history=messages, 
      deps=deps)
  
  ai_message = add_message_to_conversation(
    office.id, contact_phone_number, response.new_messages_json())

  print(f"Response: {response.data}")
    
  # send_reply(office_phone_number,
  #            contact_phone_number, 
  #            response.data, 
  #            num_media > 0, 
  #            ai_message.id, 
  #            twilio_client, 
  #            openai_client)


def main():
    kafka_broker = os.getenv('KAFKA_BROKER')
    kafka_client_id = os.getenv('KAFKA_CLIENT_ID')
    kafka_group_id = os.getenv('KAFKA_GROUP_ID')
    kafka_security_protocol = os.getenv('KAFKA_SECURITY_PROTOCOL')
    kafka_sasl_username = os.getenv('KAFKA_USER')
    kafka_sasl_password = os.getenv('KAFKA_PASSWORD')
    kafka_sasl_mechanism = os.getenv('KAFKA_SASL_MECHANISM')
    consumer = KafkaConsumer(
        'process_message', 
        bootstrap_servers=kafka_broker, 
        api_version=(3, 9, 0),
        client_id=kafka_client_id if kafka_client_id else "health_up",
        security_protocol=kafka_security_protocol if kafka_security_protocol else "PLAINTEXT",
        sasl_mechanism=kafka_sasl_mechanism,
        sasl_plain_username=kafka_sasl_username,
        sasl_plain_password=kafka_sasl_password,
        auto_offset_reset = 'earliest',
        enable_auto_commit = False,
        value_deserializer=lambda m: json.loads(m.decode('ascii')))
    for msg in consumer:
        handle_message(msg.value)

if __name__ == "__main__":
  logger.info("Starting Health Up Worker")
  main()
