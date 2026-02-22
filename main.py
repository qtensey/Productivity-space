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

        print(f"error: task with ID: {task_id} not found")

manager = TaskManager()

while True:
    command = input("enter command: (add, show, update, delete or exit): ")

    if command == "add":
        header = input("enter the task title: ")
        description = input("enter the task description: ")
        manager.add_task(header, description)

    elif command == "show":
        manager.show_tasks()

    elif command == "update":
        task_id = int(input("enter the task ID: "))
        id_exist = manager.is_task_exists(task_id)
        if id_exist:
            new_status = input("enter a new status ('done' 'in progress' or 'new'): ")
            manager.set_status(task_id, new_status)           
        else:
            print(f"error: task with ID: {task_id} not found")

    elif command == "delete":
        task_id = int(input("enter the task ID: "))
        manager.delete_task(task_id)

    elif command == "exit":
        break

    else:
        print("unknow command")