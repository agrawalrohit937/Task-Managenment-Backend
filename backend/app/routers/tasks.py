from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import Task
from app.models.task_status_history import TaskStatusHistory
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.utils.notification_helper import create_notification

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# ADMIN: CREATE TASK (WITH NOTIFICATION)
@router.post(
    "/",
    response_model=TaskResponse,
    dependencies=[Depends(require_role(["admin"]))],
)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):

    new_task = Task(
        title=task.title,
        description=task.description,
        assigned_to=task.assigned_to,
        status="pending",
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Create Notification
    create_notification(
        db=db,
        user_id=new_task.assigned_to,
        title="New Task Assigned",
        message=f"You have been assigned task: {new_task.title}"
    )

    return new_task

# USER: VIEW OWN TASKS
@router.get("/my", response_model=list[TaskResponse])
def get_my_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Task).filter(
        Task.assigned_to == current_user.id
    ).all()

# ADMIN + EMPLOYEE: UPDATE STATUS (WITH HISTORY + NOTIFICATION)
@router.put("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    #  RBAC
    if current_user.role != "admin" and task.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Save History
    history = TaskStatusHistory(
        task_id=task.id,
        old_status=task.status,
        new_status=task_data.status,
        changed_by=current_user.id,
    )

    task.status = task_data.status

    db.add(history)
    db.commit()
    db.refresh(task)

    # Notification using helper
    create_notification(
        db=db,
        user_id=task.assigned_to,
        title="Task Status Updated",
        message=f"Task '{task.title}' status changed to {task_data.status}",
    )

    return task

@router.get("/{task_id}/history")
def get_task_history(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    history = db.query(TaskStatusHistory).filter(
        TaskStatusHistory.task_id == task_id
    ).all()

    if not history:
        raise HTTPException(status_code=404, detail="No history found")

    return history
