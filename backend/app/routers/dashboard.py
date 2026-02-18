from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.task import Task
from app.models.user import User
from app.models.notification import Notification
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# USER DASHBOARD
@router.get("/me")
def user_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    total_tasks = db.query(Task).filter(
        Task.assigned_to == current_user.id
    ).count()

    completed_tasks = db.query(Task).filter(
        Task.assigned_to == current_user.id,
        Task.status == "completed"
    ).count()

    pending_tasks = db.query(Task).filter(
        Task.assigned_to == current_user.id,
        Task.status != "completed"
    ).count()

    unread_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "unread_notifications": unread_notifications
    }


# ADMIN DASHBOARD
@router.get("/admin")
def admin_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    total_users = db.query(User).count()
    total_tasks = db.query(Task).count()

    completed_tasks = db.query(Task).filter(
        Task.status == "completed"
    ).count()

    pending_tasks = db.query(Task).filter(
        Task.status != "completed"
    ).count()

    return {
        "total_users": total_users,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks
    }
