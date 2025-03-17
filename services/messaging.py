import os
import openai
import logging
from twilio.rest import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_text(from_number, to_number, message, twilio_client: Client):
  response = twilio_client.messages.create(
      from_=f"whatsapp:{from_number}",
      body=message,
      to=f"whatsapp:{to_number}",
  )
  return response

def send_audio(from_number, to_number, message, ai_response_id, 
               media_path: str, twilio_client: Client, openai_client: openai.OpenAI):
  speech_audio_file = f"{ai_response_id}.mp3"
  speech_file_path = f"{media_path}/{speech_audio_file}"
  
  response = openai_client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=message
  )
  
  response.write_to_file(speech_file_path)
  
  response = twilio_client.messages.create(
      from_=f"whatsapp:{from_number}",
      media_url=[f"https://healthup.loclx.io/medias/{speech_audio_file}"],
      body=message,
      to=f"whatsapp:{to_number}",
  )
  
  return response

def send_reply(from_number, to_number, body_text, is_media, ai_response_id, 
              media_path: str, twilio_client: Client, openai_client: openai.OpenAI):
  try:
      max_length = 1600
      # Calculate the number of messages
      num_messages = len(body_text) // max_length + (1 if len(body_text) % max_length > 0 else 0)
    
      for i in range(num_messages):
          # Calculate start and end indices for the substring
          start_index = i * max_length
          end_index = start_index + max_length

          # Get the substring for the current chunk
          message_chunk = body_text[start_index:end_index]
          
          response = send_text(from_number, to_number, message_chunk, twilio_client)
          # if is_media:
          #   response = send_audio(from_number, to_number, message_chunk, 
          #                         ai_response_id, media_path, twilio_client, openai_client)
          # else:
          #   response = send_text(from_number, to_number, message_chunk, twilio_client)

          logger.info(f"Message {i + 1}/{num_messages} sent from {from_number} to {to_number}: {response.sid}")

  except Exception as e:
      logger.error(f"Error sending message to {to_number}: {e}")