from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError, MultipleResultsFound, DataError
from models import User, Task
from exceptions import DomainError, DuplicateResourceError, ResourceNotFoundError

def get_user_by_username(db: Session, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    try:
        return db.scalar_one_or_none(stmt)
    except MultipleResultsFound as e:
        raise DuplicateResourceError(f"Critical error: duplicates found for {username}") from e

def create_user(db: Session, username: str, email: str, hashed_password: str) -> User:
    new_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError as e:
        db.rollback()
        raise DuplicateResourceError("A user with this username or email already exists.") from e
    except Exception:
        db.rollback()
        raise

def create_task(db: Session, header: str, description: str, user_id: int) -> Task:
    new_task = Task(header=header, description=description, user_id=user_id)
    db.add(new_task)
    try:
        db.commit()
        db.refresh(new_task)
        return new_task
    except IntegrityError as e:
        db.rollback()
        raise ResourceNotFoundError(f"Unable to create task: user with ID {user_id} does not exists.") from e
    except Exception:
        db.rollback()
        raise

def get_all_tasks(db: Session, user_id: int) -> list[Task]:
    stmt = select(Task).where(Task.user_id == user_id)
    return db.scalars(stmt).all()

def update_task_status(db: Session, task_id: int, new_status: str, user_id: int) -> bool:
    stmt = (
        update(Task)
        .where(Task.id == task_id,
               Task.user_id == user_id)
        .values(status=new_status)
    )
    try:
        result = db.execute(stmt)
        db.commit()
        return result.rowcount > 0
    except (IntegrityError, DataError) as e:
        db.rollback()
        raise DomainError(f"Unable to update status: DB constraint conflict for value '{new_status}'") from e
    except Exception:
        db.rollback()
        raise
    
def delete_task(db: Session, task_id: int, user_id: int) -> bool:
    stmt = (
        delete(Task)
        .where(Task.id == task_id,
               Task.user_id == user_id)
    )
    try:
        result = db.execute(stmt)
        db.commit()
        return result.rowcount > 0
    except Exception:
        db.rollback()
        raise

def get_user_by_id(db: Session, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    return db.scalar_one_or_none(stmt)