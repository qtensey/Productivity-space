from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from manager import TaskManager
from pydantic import BaseModel
from typing import Literal

app = FastAPI(title="Task Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskCreate(BaseModel):
    header: str
    description: str

class TaskStatusUpdate(BaseModel):
    status: Literal["new", "in progress", "done"]

def get_manager():
    manager = TaskManager()
    try:
        yield manager
    finally:
        manager.close()

@app.get("/tasks")
def get_tasks(manager: TaskManager = Depends(get_manager)):
    return manager.get_all_tasks()

@app.post("/tasks")
def create_task(new_task: TaskCreate, manager: TaskManager = Depends(get_manager)):
    return manager.add_task(new_task.header, new_task.description)

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, manager: TaskManager = Depends(get_manager)):
    if not manager.if_task_exists(task_id):
        raise HTTPException(status_code=404, detail="task not found")
    manager.delete_task(task_id)
    return {"message": f"task with ID {task_id} successfully deleted"}

@app.patch("/tasks/{task_id}")
def update_task_status(task_id: int, update_data: TaskStatusUpdate, manager: TaskManager = Depends(get_manager)):

    if not manager.if_task_exists(task_id):
        raise HTTPException(status_code=404, detail="Task not found")

    manager.set_status(task_id, update_data.status)

    return {
        "message": f"Task status {task_id} successfully updated",
        "new_status": update_data.status
    }