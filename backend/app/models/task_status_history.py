from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base


class TaskStatusHistory(Base):
    __tablename__ = "task_status_history"

    id = Column(Integer, primary_key=True, index=True)

    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    old_status = Column(String, nullable=False)
    new_status = Column(String, nullable=False)

    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
