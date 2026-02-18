from pydantic import BaseModel
from typing import Optional
from enum import Enum

#  Enum for task status (BEST PRACTICE)
class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: int


class TaskUpdate(BaseModel):
    status: TaskStatus


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    assigned_to: int

    class Config:
        from_attributes = True


# REQUIRED FOR PYDANTIC v2 (VERY IMPORTANT)
TaskUpdate.model_rebuild()
TaskResponse.model_rebuild()
