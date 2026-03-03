from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from manager import TaskManager
from pydantic import BaseModel

app = FastAPI(title="Task Manager API")
manager = TaskManager()

# налаштування CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Дозволяємо запити з будь-яких джерел (для розробки)
    allow_credentials=True,
    allow_methods=["*"], # Дозволяємо GET, POST, DELETE, PATCH
    allow_headers=["*"],
)

class TaskCreate(BaseModel):
    header: str
    description: str

class TaskStatusUpdate(BaseModel):
    status: str

@app.get("/")
def read_root():
    return {"message": "hello!"}

@app.get("/tasks")
def get_tasks():
    return manager.get_all_tasks()

@app.post("/tasks")
def create_task(new_task: TaskCreate):
    return manager.add_task(new_task.header, new_task.description)

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    if not manager.if_task_exists(task_id):
        raise HTTPException(status_code=404, detail="task not found")
    manager.delete_task(task_id)
    return {"message": f"task with ID {task_id} successfully deleted"}

@app.patch("/tasks/{task_id}")
def update_task_status(task_id: int, update_data: TaskStatusUpdate):

    if not manager.if_task_exists(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    
    valid_statuses = ["new", "in progress", "done"]

    if update_data.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Choose: 'new', 'in progress', 'done'"
        )

    manager.set_status(task_id, update_data.status)

    return {
        "message": f"Task status {task_id} successfully updated",
        "new_status": update_data.status
    }

