import datetime
from uuid_extensions import uuid7str
from database import engine
from sqlmodel import (
    select,
    Session
)
from models import (
    ChatMessage
)
from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
)
    
def get_conversation_messages(office_id: str, from_number: str) -> list[ModelMessage]:
    with Session(engine) as session:
        messages: list[ModelMessage] = []
        statement = select(ChatMessage)
        statement = statement.where(ChatMessage.office_id == office_id)
        statement = statement.where(ChatMessage.phone_number == from_number)
        statement = statement.limit(1)
        statement = statement.order_by(ChatMessage.timestamp.asc())
        results = session.exec(statement)
        for message in results:
            messages.extend(ModelMessagesTypeAdapter.validate_json(message.content))

        actual_date_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
        statement = select(ChatMessage)
        statement = statement.where(ChatMessage.phone_number == from_number)
        statement = statement.where(ChatMessage.timestamp < actual_date_time)
        statement = statement.limit(10)
        statement = statement.order_by(ChatMessage.timestamp.asc())
        results = session.exec(statement)
        
        for message in results:
            messages.extend(ModelMessagesTypeAdapter.validate_json(message.content))
            
        return messages
      
def add_message_to_conversation(office_id: str, from_number: str, content: str):
    with Session(engine, expire_on_commit=False) as session:  
      message = ChatMessage(
        id=uuid7str(),
        office_id=office_id,
        phone_number=from_number, 
        timestamp=datetime.datetime.now().isoformat(), 
        content=content)
      session.add(message)
      session.commit()
      return message
