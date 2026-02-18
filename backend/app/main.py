from fastapi import FastAPI

from app.routers import auth, tasks, notifications, dashboard

app = FastAPI(
    title="Task Management System",
    description="FastAPI Task Management with Auth & RBAC",
    version="1.0.0"
)

# include routers
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(notifications.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"message": "Task Management System API running"}
