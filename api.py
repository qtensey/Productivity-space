from fastapi import FastAPI, HTTPException, Depends, status, Response, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Literal, Optional
from security import get_password_hash, verify_password, create_access_token, ALGORITHM, SECRET_KEY
import jwt
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from database import get_db
import crud
from database import Base, engine
import models
from exceptions import DomainError, DuplicateResourceError, ResourceNotFoundError

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Task Manager API", lifespan=lifespan)

@app.exception_handler(DuplicateResourceError)
async def duplicate_resource_handler(request: Request, exc: DuplicateResourceError):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})

@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})

@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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

    model_config = ConfigDict(from_attributes=True)

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

    model_config = ConfigDict(from_attributes=True)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        
        user_id = int(user_id_str)
        user = crud.get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")
        
        return int(user_id_str)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user)):
    return crud.get_all_tasks(db, current_user_id)

@app.post("/tasks", response_model=TaskResponse)
def create_task(
    new_task: TaskCreate,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.create_task(
        db,
        header=new_task.header,
        description=new_task.description,
        user_id=current_user_id
    )

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = crud.delete_task(db, task_id=task_id, user_id=current_user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Task not found.")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.patch("/tasks/{task_id}", response_model=MessageResponse)
def update_task_status(
    task_id: int,
    update_data: TaskStatusUpdate,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = crud.update_task_status(db, task_id=task_id, new_status=update_data.status, user_id=current_user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Task not found or access denied")
    
    return MessageResponse(
        message=f"Task status {task_id} successfully updated",
        new_status=update_data.status
    )
    
@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(new_user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(new_user.password)
    return crud.create_user(
        db,
        username=new_user.username,
        email=new_user.email,
        hashed_password=hashed_password
    )

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, form_data.username)

    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if verify_password(form_data.password, user.hashed_password) is False:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}