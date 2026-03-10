import sqlite3
from pathlib import Path
from models import Task
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
db_path = DATA_DIR / "database.db"

class TaskNotFoundError(Exception):
    pass

class UserAlreadyExistsError(Exception):
    pass

def initialize_database():
    """Create tables when the program is first run"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            header TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'new',
            created_at TEXT,
                   
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()

initialize_database()

class TaskManager:
    def __init__(self):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")

    def add_task(self, header: str, description: str):
        current_time = str(datetime.now())
        
        self.cursor.execute("""
            INSERT INTO tasks (header, description, created_at)
            VALUES (?, ?, ?) 
            RETURNING id, header, description, status, created_at
        """, (header, description, current_time))
        
        row = self.cursor.fetchone()
        self.conn.commit()
        
        task = Task(**dict(row))
        return task.to_dict()

    def set_status(self, task_id: int, new_status: str):
        self.cursor.execute(""" 
            UPDATE tasks
            SET status = ?
            WHERE id = ?
        """, (new_status, task_id))
        
        if self.cursor.rowcount == 0:
            raise TaskNotFoundError(f"Task with id {task_id} not found.")
            
        self.conn.commit()

    def delete_task(self, task_id: int):
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id, ))
        
        if self.cursor.rowcount == 0:
            raise TaskNotFoundError(f"Task with id {task_id} not found.")
            
        self.conn.commit()

    def get_all_tasks(self):
        self.cursor.execute("SELECT * FROM tasks")
        rows = self.cursor.fetchall()
        
        return [Task(**dict(row)).to_dict() for row in rows]

    def close(self):
        self.cursor.close()
        self.conn.close()


class UserManager:
    def __init__(self):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row 
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")

    def create_user(self, username: str, email: str, hashed_password: str):
        try:
            self.cursor.execute("""
                INSERT INTO users (username, email, hashed_password)
                VALUES (?, ?, ?)
                RETURNING id, username, email
            """, (username, email, hashed_password))
            row = self.cursor.fetchone()
            self.conn.commit()
            return dict(row)
        except sqlite3.IntegrityError:
            raise UserAlreadyExistsError
        
    def get_user_by_username(self, username: str):
        self.cursor.execute("""
            SELECT * FROM users
            WHERE username = ?
        """, (username,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        return dict(row)
    
    def close(self):
        self.cursor.close()
        self.conn.close()