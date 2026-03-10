from fastapi import FastAPI, HTTPException, Depends, status, Response
from fastapi.middleware.cors import CORSMiddleware
from manager import TaskManager, UserManager, TaskNotFoundError, UserAlreadyExistsError
from pydantic import BaseModel, Field, EmailStr
from typing import Literal, Optional
from security import get_password_hash

app = FastAPI(title="Task Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TaskStatuses = Literal["new", "in progress", "done"]


class TaskCreate(BaseModel):
    header: str = Field(..., min_length=3, max_length=100, description="Short title of the task")
    description: str = Field(..., max_length=2000)


class TaskStatusUpdate(BaseModel):
    status: TaskStatuses


class TaskResponse(BaseModel):
    id: int
    header: str
    description: str
    status: TaskStatuses
    created_at: str


class MessageResponse(BaseModel):
    message: str
    new_status: Optional[str] = None


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=14)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr


def get_task_manager():
    manager = TaskManager()
    try:
        yield manager
    finally:
        manager.close()

def get_user_manager():
    manager = UserManager()
    try:
        yield manager
    finally:
        manager.close()

@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(manager: TaskManager = Depends(get_task_manager)):
    return manager.get_all_tasks()

@app.post("/tasks", response_model=TaskResponse)
def create_task(new_task: TaskCreate, manager: TaskManager = Depends(get_task_manager)):
    return manager.add_task(new_task.header, new_task.description)

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, manager: TaskManager = Depends(get_task_manager)):
    try:
        manager.delete_task(task_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")

@app.patch("/tasks/{task_id}", response_model=MessageResponse)
def update_task_status(task_id: int, update_data: TaskStatusUpdate, manager: TaskManager = Depends(get_task_manager)):
    try:
        manager.set_status(task_id, update_data.status)
        return MessageResponse(
            message=f"Task status {task_id} successfully updated",
            new_status=update_data.status
        )
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")
    
@app.post("/register", response_model=UserResponse)
def create_user(new_user: UserCreate, manager: UserManager = Depends(get_user_manager)):
    hashed_password = get_password_hash(new_user.password)
    try:
        return manager.create_user(username=new_user.username, email=new_user.email, hashed_password=hashed_password)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=400, detail="User with this username or email already exists")