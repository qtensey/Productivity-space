from manager import TaskManager

def update_function(task_manager: TaskManager) -> None:
    try:
        task_id = int(input("enter the task ID: "))
    except ValueError:
        print("id must be a number")
        return
    id_exist = task_manager.if_task_exists(task_id)
    if id_exist:
        new_status = input("enter a new status ('done' 'in progress' or 'new'): ")
        task_manager.set_status(task_id, new_status)
        print("status updated successfully")
    else:
        print(f"error: task with ID: {task_id} not found")

def delete_function(task_manager: TaskManager) -> None:
    try:
        task_id = int(input("enter the task ID: "))
    except ValueError:
        print("id must be a number")
        return
    task_manager.delete_task(task_id)

def main():
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
            update_function(manager)
        elif command == "delete":
            delete_function(manager)
        elif command == "exit":
            break
        else:
            print("unknow command")

if __name__ == "__main__":
    main()