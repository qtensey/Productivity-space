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


