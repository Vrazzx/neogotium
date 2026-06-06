from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .models import PriorityEnum, StatusEnum

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    status: StatusEnum = StatusEnum.todo
    priority: PriorityEnum = PriorityEnum.medium
    tag: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    status: Optional[StatusEnum] = None
    priority: Optional[PriorityEnum] = None
    tag: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskOut(BaseModel):
    id: int
    board_id: int
    title: str
    description: Optional[str]
    assignee: Optional[str]
    status: StatusEnum
    priority: PriorityEnum
    tag: Optional[str]
    created_by_ai: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BoardCreate(BaseModel):
    name: str
    telegram_chat_id: Optional[str] = None

class BoardOut(BaseModel):
    id: int
    name: str
    telegram_chat_id: Optional[str]
    tasks: list[TaskOut] = []

    class Config:
        from_attributes = True

# Для AI-парсера
class ParsedTask(BaseModel):
    is_task: bool
    title: str = ""
    assignee: str = ""
    priority: PriorityEnum = PriorityEnum.medium
    tag: str = "feat"
    confidence: float = 0.0  # 0..1, насколько AI уверен