import json
from pathlib import Path
from models import Task

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
tasks_path = DATA_DIR / "tasks.json"

class TaskManager:

    def __init__(self):
        self.tasks = []
        self.load_from_file()
    
    def load_from_file(self):
        if tasks_path.exists():
            with open(tasks_path, 'r', encoding="utf-8") as file:
                load_tasks = json.load(file)
                for task in load_tasks:
                    load_task = Task(task["id"], task["header"], task["description"], task["status"], task["created_at"])
                    self.tasks.append(load_task)

    def add_task(self, header: str, description: str):
        if len(self.tasks) == 0:
            new_id = 1
        else:
            new_id = max([task.id for task in self.tasks]) + 1
        new_task = Task(new_id, header, description)
        self.tasks.append(new_task)

    def show_tasks(self):
        if len(self.tasks) == 0:
            print("tasks not found")
        else:
            for task in self.tasks:
                print(task)

    def delete_task(self, task_id: int):
        for task in self.tasks:
            if task.id == task_id:
                self.tasks.remove(task)
                print(f"task {task_id} successfully deleted")
                return
        print(f"error: task with ID: {task_id} not found")

    def is_task_exists(self, task_id: int):
        for task in self.tasks:
            if task.id == task_id:
                return True
        return False

    def set_status(self, task_id: int, new_status: str):
        if new_status in ["done", "in progress", "new"]:
            for task in self.tasks:
                if task.id == task_id:
                    task.status = new_status
                    print("task status updated")
                    return
        else:
            print("status should be 'new', 'done' or 'in progress'")
            return

    def save_to_file(self) -> None:
        data_to_save = []
        for task in self.tasks:
            data_to_save.append(task.to_dict())
        with open(tasks_path, "w", encoding="utf-8") as file:
            json.dump(data_to_save, file, indent=4, ensure_ascii=False)