from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500))
    status = Column(String(50), default="pending")
    priority = Column(String(50), default="medium")
    assigned_to = Column(Integer, ForeignKey("users.id"))
