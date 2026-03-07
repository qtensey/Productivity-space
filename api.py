from fastapi import FastAPI, HTTPException, Depends, status, Response
from fastapi.middleware.cors import CORSMiddleware
from manager import TaskManager, TaskNotFoundError
from pydantic import BaseModel, Field
from typing import Literal, Optional

app = FastAPI(title="Task Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TaskStatus = Literal["new", "in progress", "done"]

class TaskCreate(BaseModel):
    header: str = Field(..., min_length=3, max_length=100, description="Short title of the task")
    description: str = Field(..., max_length=2000)


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskResponse(BaseModel):
    id: int
    header: str
    description: str
    status: TaskStatus
    created_at: str


class MessageResponse(BaseModel):
    message: str
    new_status: Optional[str] = None


def get_manager():
    manager = TaskManager()
    try:
        yield manager
    finally:
        manager.close()

@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(manager: TaskManager = Depends(get_manager)):
    return manager.get_all_tasks()

@app.post("/tasks", response_model=TaskResponse)
def create_task(new_task: TaskCreate, manager: TaskManager = Depends(get_manager)):
    return manager.add_task(new_task.header, new_task.description)

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, manager: TaskManager = Depends(get_manager)):
    try:
        manager.delete_task(task_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")

@app.patch("/tasks/{task_id}", response_model=MessageResponse)
def update_task_status(task_id: int, update_data: TaskStatusUpdate, manager: TaskManager = Depends(get_manager)):
    try:
        manager.set_status(task_id, update_data.status)
        return MessageResponse(
            message=f"Task status {task_id} successfully updated",
            new_status=update_data.status
        )
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")