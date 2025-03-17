import datetime
import pytz
import logging
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from models import (
    Office,
    Manager,
    OfficeInventory
)

from services.office import (
  find_office_by_id,
)

from services.manager import (
  find_manager_by_id,
)

logger = logging.getLogger('health_up:manager_agent')
logger.setLevel(logging.CRITICAL)

@dataclass
class ManagerDependencies:
    office_id: str
    manager_id: str
    manager_phone_number: str

# ollama_model = OpenAIModel(
#     model_name='llama3.2', provider=OpenAIProvider(base_url='http://localhost:11434/v1')
# )   

manager_agent = Agent("openai:gpt-4o-mini", system_prompt="""
                You are a secretary in a dental office. Perform the following steps:
                1. Remember manager can use word 'menu' to see the menu.                
                2. Use the `get_manager` tool to retrieve doctor info from database.
                3. Use the `get_office_inventory` tool to retrieve office inventory from database.
                4. When greeting manager, please greet manager by his name. How can I help you? Show a list of available commands:
                    1. List inventory
              """)

@manager_agent.tool_plain
def current_date_time() -> str:
    logger.info("Add date and time...")
    tz = pytz.timezone('America/Sao_Paulo')
    return f"Current date and time is: {datetime.datetime.now(tz).strftime("%Y-%m-%dT%H:%M:%S %Z")}"
  
@manager_agent.tool
def get_office_info(ctx: RunContext[ManagerDependencies]) -> Office:
    logger.info("Get office info...")
    return find_office_by_id(ctx.deps.office_id)
  
@manager_agent.tool
def get_office_inventory(ctx: RunContext[ManagerDependencies]) -> OfficeInventory:
    logger.info("Get office info...")
    inventories: list[OfficeInventory] = []
    inventories.append(OfficeInventory(name='toothbrush', description='toothbrush', quantity=100))
    inventories.append(OfficeInventory(name='toothpaste', description='toothpaste', quantity=100))
    inventories.append(OfficeInventory(name='dental floss', description='dental floss', quantity=100))
    return inventories
      
@manager_agent.tool  
def get_manager(ctx: RunContext[ManagerDependencies]) -> Manager:
    logger.info("Get office info...")
    return find_manager_by_id(ctx.deps.manager_id)

