from src.srex.models.tasks import Tasks
from src.srex.models.hosts import Hosts


from pydantic import BaseModel

class Play(BaseModel):
    name: str
    hosts: Hosts
    tasks: Tasks
