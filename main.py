import openai
import json
from kafka import KafkaConsumer
from decouple import config
from twilio.rest import Client
from services.media import transcribe_media
from services.messaging import send_reply

account_sid = config("TWILIO_ACCOUNT_SID")
auth_token = config("TWILIO_AUTH_TOKEN")

twilio_client = Client(account_sid, auth_token)
openai_client = openai.OpenAI(api_key=config("OPENAI_API_KEY"))

def handle_message(message):
  content = message["body"]
  num_media = int(message["num_media"] or 0)
  if num_media > 0:
      media_url = message["media_url"]
      mime_type = message["media_type"]
      content = transcribe_media(media_url, mime_type, twilio_client, openai_client)
  
  chat_response = "no data"
  response = openai_client.chat.completions.create(
      model="gpt-4-turbo",
      messages=[{"role": "system", "content": "Your system message here, if any"},
                {"role": "user", "content": content}],
      stream=False
  )

  if response.choices and response.choices[0].message.content:
      chat_response = response.choices[0].message.content
  
  send_reply(message["from_number"], chat_response, num_media > 0, response.id, twilio_client, openai_client)


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
  main()
