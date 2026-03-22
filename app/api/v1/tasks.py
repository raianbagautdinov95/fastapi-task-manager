from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.enums import TaskStatus

from app.crud.project import crud_project
from app.crud.task import crud_task
from app.db.session import get_session
from app.deps import get_current_user
from app.models.user import User
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


def can_access_project(current_user: User, owner_id: int) -> bool:
    return current_user.id == owner_id or current_user.is_admin


def can_manage_task(current_user: User, project_owner_id: int, assignee_id: int | None) -> bool:
    return (
        current_user.id == project_owner_id
        or current_user.is_admin
        or current_user.id == assignee_id
    )


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    project = await crud_project.get_by_id(session, data.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not can_access_project(current_user, project.owner_id):
        raise HTTPException(status_code=403, detail="Access denied")

    return await crud_task.create(session, data, creator_id=current_user.id)


@router.get("/", response_model=list[TaskRead])
async def get_tasks(
    project_id: int = Query(...),
    status_filter: TaskStatus | None = Query(None, alias="status"),
    assignee_id: int | None = Query(None),
    creator_id: int | None = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    project = await crud_project.get_by_id(session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not can_access_project(current_user, project.owner_id):
        raise HTTPException(status_code=403, detail="Access denied")

    return await crud_task.get_filtered(
        session,
        project_id=project_id,
        status=status_filter,
        assignee_id=assignee_id,
        creator_id=creator_id,
    )


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    task = await crud_task.get_by_id(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    project = await crud_project.get_by_id(session, task.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not can_manage_task(current_user, project.owner_id, task.assignee_id):
        raise HTTPException(status_code=403, detail="Access denied")

    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    task = await crud_task.get_by_id(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    project = await crud_project.get_by_id(session, task.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not can_manage_task(current_user, project.owner_id, task.assignee_id):
        raise HTTPException(status_code=403, detail="Access denied")

    return await crud_task.update(session, task, data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    task = await crud_task.get_by_id(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    project = await crud_project.get_by_id(session, task.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not can_manage_task(current_user, project.owner_id, task.assignee_id):
        raise HTTPException(status_code=403, detail="Access denied")

    await crud_task.delete(session, task)