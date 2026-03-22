from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.enums import TaskStatus
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskCRUD:
    async def create(
        self,
        session: AsyncSession,
        data: TaskCreate,
        creator_id: int,
    ) -> Task:
        task = Task(
            title=data.title,
            description=data.description,
            status=data.status,
            project_id=data.project_id,
            creator_id=creator_id,
            assignee_id=data.assignee_id,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task

    async def get_by_id(
        self,
        session: AsyncSession,
        task_id: int,
    ) -> Task | None:
        result = await session.execute(
            select(Task).where(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_filtered(
            self,
            session: AsyncSession,
            project_id: int,
            status: TaskStatus | None = None,
            assignee_id: int | None = None,
            creator_id: int | None = None,
    ) -> list[Task]:
        query = select(Task).where(Task.project_id == project_id)

        if status:
            query = query.where(Task.status == status)

        if assignee_id is not None:
            query = query.where(Task.assignee_id == assignee_id)

        if creator_id is not None:
            query = query.where(Task.creator_id == creator_id)

        result = await session.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        session: AsyncSession,
        task: Task,
        data: TaskUpdate,
    ) -> Task:
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(task, field, value)

        await session.commit()
        await session.refresh(task)
        return task

    async def delete(
        self,
        session: AsyncSession,
        task: Task,
    ) -> None:
        await session.delete(task)
        await session.commit()


crud_task = TaskCRUD()