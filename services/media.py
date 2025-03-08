import openai
import os
import mimetypes
import requests
from twilio.rest import Client
from urllib.parse import urlparse

def transcribe_media(media_url, media_path, mime_type, 
                     twilio_client: Client, openai_client: openai.OpenAI):
  file_extension = mimetypes.guess_extension(mime_type)
  media_sid = os.path.basename(urlparse(media_url).path)
  content = requests.get(
    media_url, 
    auth=(twilio_client.account_sid, twilio_client.password), 
    stream=True
  ).raw.read()
  filename = '{path}/{sid}{ext}'.format(path=media_path, sid=media_sid, ext=file_extension)
  with open(filename, 'wb') as fd:
    fd.write(content)
  
  response = openai_client.audio.transcriptions.create(
      model="whisper-1",
      file=open(filename, "rb"),
      response_format="text"
  )
  return response