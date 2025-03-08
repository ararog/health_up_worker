import datetime
import logging
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from models import (
    Office,
    Appointment,
    Patient,
    Doctor,
    Speciality,
)

logger = logging.getLogger('health_up:owner_agent')
logger.setLevel(logging.CRITICAL)

@dataclass
class OwnerDependencies:
    office_id: str
    owner_id: str
    owner_phone_number: str

system_date_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")

owner_agent = Agent('openai:gpt-4o', system_prompt="""
                Current date and time is: %s
                You are a secretary in a dental office. Perform the following steps:
                1. Use the `get_office_info` tool to retrieve office info from database.
              """ % system_date_time)

#@owner_agent.tool
#def get_office_info(ctx: RunContext[OwnerDependencies]) -> Office:
#    logger.info("Get office info...")
#    return find_office_by_id(ctx.deps.office_id)
