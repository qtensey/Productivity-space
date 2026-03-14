from fastapi import FastAPI, HTTPException, Depends, status, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from manager import TaskManager, UserManager, TaskNotFoundError, UserAlreadyExistsError
from pydantic import BaseModel, Field, EmailStr
from typing import Literal, Optional
from security import get_password_hash, verify_password, create_access_token, ALGORITHM, SECRET_KEY
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        
        return int(user_id_str)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(
    manager: TaskManager = Depends(get_task_manager),
    current_user_id: int = Depends(get_current_user)
):
    return manager.get_all_tasks(current_user_id)

@app.post("/tasks", response_model=TaskResponse)
def create_task(
    new_task: TaskCreate,
    current_user_id: int = Depends(get_current_user),
    manager: TaskManager = Depends(get_task_manager)
):
    return manager.add_task(new_task.header, new_task.description, current_user_id)

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user_id: int = Depends(get_current_user),
    manager: TaskManager = Depends(get_task_manager)
):
    try:
        manager.delete_task(task_id, current_user_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")

@app.patch("/tasks/{task_id}", response_model=MessageResponse)
def update_task_status(
    task_id: int,
    update_data: TaskStatusUpdate,
    current_user_id: int = Depends(get_current_user),
    manager: TaskManager = Depends(get_task_manager)
):
    try:
        manager.set_status(task_id, update_data.status, current_user_id)
        return MessageResponse(
            message=f"Task status {task_id} successfully updated",
            new_status=update_data.status
        )
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")
    
@app.post("/register", response_model=UserResponse)
def register(new_user: UserCreate, manager: UserManager = Depends(get_user_manager)):
    hashed_password = get_password_hash(new_user.password)
    try:
        return manager.create_user(username=new_user.username, email=new_user.email, hashed_password=hashed_password)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=400, detail="User with this username or email already exists")
    
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), manager: UserManager = Depends(get_user_manager)):
    user = manager.get_user_by_username(form_data.username)
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if verify_password(form_data.password, user["hashed_password"]) is False:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": str(user["id"])})
    return {"access_token": access_token, "token_type": "bearer"}