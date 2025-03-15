import datetime
import logging
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from models import (
    Office,
    Owner,
    OfficeRevenue,
    OfficePopularServices
)

from services.office import (
  find_office_by_id,
)

from services.owner import (
  find_owner_by_id,
)

logger = logging.getLogger('health_up:owner_agent')
logger.setLevel(logging.CRITICAL)

@dataclass
class OwnerDependencies:
    office_id: str
    owner_id: str
    owner_phone_number: str

# ollama_model = OpenAIModel(
#     model_name='llama3.2', provider=OpenAIProvider(base_url='http://localhost:11434/v1')
# )   

owner_agent = Agent('openai:gpt-4o', system_prompt="""
                You are a secretary in a dental office. Perform the following steps:
                1. Remember owner can use word 'menu' to see the menu.                
                2. Use the `get_owner` tool to retrieve owner info from database.
                3. Use the `get_office_revenue` tool to retrieve office revenue from database.
                4. Use the `get_office_popular_services` tool to retrieve office popular services from database.
                5. When greeting owner, please greet owner by his name. How can I help you? Show a list of available commands:
                    1. Show revenue
                    2. List most popular services
              """)

@owner_agent.tool_plain
def current_date_time() -> str:
    logger.info("Add date and time...")
    return f"Current date and time is: {datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")}"
  
@owner_agent.tool
def get_office_info(ctx: RunContext[OwnerDependencies]) -> Office:
    logger.info("Get office info...")
    return find_office_by_id(ctx.deps.office_id)

@owner_agent.tool
def get_owner(ctx: RunContext[OwnerDependencies]) -> Owner:
    logger.info("Get office info...")
    return find_owner_by_id(ctx.deps.owner_id)
   
@owner_agent.tool
def get_office_revenue(ctx: RunContext[OwnerDependencies]) -> OfficeRevenue:
    logger.info("Get office revenue...")
    revenues: list[OfficeRevenue] = []
    revenues.append(OfficeRevenue(date='2025-03-01', revenue=1000))
    revenues.append(OfficeRevenue(date='2025-03-02', revenue=2000))
    revenues.append(OfficeRevenue(date='2025-03-03', revenue=3000))
    return revenues

@owner_agent.tool
def get_office_popular_services(ctx: RunContext[OwnerDependencies]) -> OfficePopularServices:
    logger.info("Get office info...")
    services: list[OfficePopularServices] = []
    services.append(OfficePopularServices(name='Dental Cleaning', count=100))
    services.append(OfficePopularServices(name='Dental Filling', count=50))
    services.append(OfficePopularServices(name='Dental Extraction', count=20))
    return services