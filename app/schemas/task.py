from pydantic import BaseModel, ConfigDict

from app.models.enums import TaskStatus


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.todo


class TaskCreate(TaskBase):
    project_id: int
    assignee_id: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    assignee_id: int | None = None


class TaskRead(TaskBase):
    id: int
    project_id: int
    creator_id: int
    assignee_id: int | None = None

    model_config = ConfigDict(from_attributes=True)