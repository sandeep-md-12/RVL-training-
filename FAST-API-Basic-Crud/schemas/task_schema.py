from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

# Common properties
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[int] = 1

    class Config:
        from_attributes = True

# Data needed to CREATE a task
class TaskCreate(TaskBase):
    pass

# Data returned to the USER
class TaskResponse(TaskBase):
    id: int
    is_completed: Optional[bool] = False
    is_active: Optional[bool] = True
    created_at: datetime

class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    is_completed: Optional[bool] = None
    