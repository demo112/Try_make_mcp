from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class StageEnum(str, Enum):
    INIT = "Init"
    ALIGN = "Align"
    ARCHITECT = "Architect"
    ATOMIZE = "Atomize"
    APPROVE = "Approve"
    AUTOMATE = "Automate"
    ASSESS = "Assess"
    EXTEND = "Extend"
    DONE = "Done"

class WorkflowState(BaseModel):
    project_name: str
    current_stage: StageEnum = StageEnum.INIT
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    # Map stage name to list of created files
    documents: Dict[str, List[str]] = Field(default_factory=dict)
    
    def update_timestamp(self):
        self.updated_at = datetime.now()
