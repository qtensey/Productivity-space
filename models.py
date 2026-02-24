from datetime import datetime


class Task:

    def __init__(self, id: int, header: str, description: str, status: str = "new", created_at = None):
        self.id = id
        self.header = header
        self.description = description
        self.status = status
        
        if created_at is None:
            self.created_at = datetime.now()
        elif isinstance(created_at, str):
            self.created_at = datetime.fromisoformat(created_at)
        else:
            self.created_at = created_at
    
    def __str__(self):
        return f"[{self.id}] {self.header} | status: {self.status} | created_at: {self.created_at}"

    def to_dict(self):
        return {
            "id": self.id,
            "header": self.header,
            "description": self.description,
            "status": self.status,
            "created_at": str(self.created_at)
        }