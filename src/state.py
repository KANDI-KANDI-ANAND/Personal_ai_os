from typing import List, Optional, Any
from pydantic import BaseModel

class AgentState(BaseModel):
    messages: List[Any]
    intent: Optional[str] = None
    memory_results: List[str] = []
    found_memory: bool = False
    plan: Optional[str] = None
    steps: List[str] = []        
    current_step: int = 0 
