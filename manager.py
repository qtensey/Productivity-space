# import json
import sqlite3
from pathlib import Path
from models import Task
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
db_path = DATA_DIR / "database.db"

class TaskManager:

    def __init__(self):

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                header TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'new',
                created_at TEXT
            );
        """)

        self.conn.commit()

    def load_from_file(self):
        if tasks_path.exists():
            with open(tasks_path, 'r', encoding="utf-8") as file:
                load_tasks = json.load(file)
                for task in load_tasks:
                    load_task = Task(task["id"], task["header"], task["description"], task["status"], task["created_at"])
                    self.tasks.append(load_task)

    def add_task(self, header: str, description: str):
        current_time = str(datetime.now())
        
        self.cursor.execute("""
            INSERT INTO tasks (header, description, created_at)
            VALUES (?, ?, ?)
        """, (header, description, current_time))

        new_id = self.cursor.lastrowid
        self.conn.commit()
        
        self.cursor.execute("SELECT * FROM tasks WHERE id = ?", (new_id,))
        task = self.cursor.fetchone()
        task_obj = Task(*task)

        return task_obj.to_dict()

    def show_tasks(self):
        self.cursor.execute("SELECT * FROM tasks")
        rows = self.cursor.fetchall()
        if not rows:
            print("tasks not found")
            return
        for row in rows:
            task = Task(row[0], row[1], row[2], row[3], row[4])
            print(task)

    def set_status(self, task_id: int, new_status: str):
        self.cursor.execute(""" 
            UPDATE tasks
            SET status = ?
            WHERE id = ?
        """, (new_status, task_id))
        self.conn.commit()

    def delete_task(self, task_id: int):
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id, ))
        self.conn.commit()

    def if_task_exists(self, task_id: int):
        self.cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id, ))
        result = self.cursor.fetchone()
        if result:
            return True
        else:
            return False

    def close_connection(self):
        self.conn.close()

    def get_all_tasks(self):
        self.cursor.execute("SELECT * FROM tasks")
        rows = self.cursor.fetchall()

        result_list = []
        for row in rows:
            task = Task(row[0], row[1], row[2], row[3], row[4])
            result_list.append(task.to_dict())
        return result_list