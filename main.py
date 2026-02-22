from datetime import datetime


class Task:
    def __init__(self, id: int, header: str, description: str, status: str = "new"):
        self.id = id
        self.header = header
        self.description = description
        self.status = status
        self.created_at = datetime.now()
    
    def __str__(self):
        return f"[{self.id}] {self.header} | status: {self.status} | created_at: {self.created_at}"


class TaskManager:
    def __init__(self):
        self.tasks = []
    
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


