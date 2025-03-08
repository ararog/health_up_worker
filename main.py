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
logger.setLevel(logging.CRITICAL)

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
  
  office_phone_number = message["to_number"].split(':')[1]
  contact_phone_number = message["from_number"].split(':')[1]
  
  office = find_office_by_phone_number(office_phone_number)
  contact = find_contact_by_phone_number(office.id, contact_phone_number)
  
  messages = get_conversation_messages(office.id, contact_phone_number)

  if contact is None and contact.type == 'patient':        
    deps = AppointmentDependencies(office_id=office.id, patient_phone_number=contact_phone_number)    
    response = appointment_agent.run_sync(content, message_history=messages, deps=deps)
  
  ai_message = add_message_to_conversation(
    office.id, contact_phone_number, response.new_messages_json())

  #print(f"Response: {response.data}")
    
  send_reply(office_phone_number,
             contact_phone_number, 
             response.data, 
             num_media > 0, 
             ai_message.id, 
             twilio_client, 
             openai_client)


def main():
    kafka_broker = os.getenv('KAFKA_BROKER')
    consumer = KafkaConsumer(
        'process_message', 
        bootstrap_servers=kafka_broker, 
        group_id='health_up',
        value_deserializer=lambda m: json.loads(m.decode('ascii')))
    for msg in consumer:
        handle_message(msg.value)

if __name__ == "__main__":
  main()
