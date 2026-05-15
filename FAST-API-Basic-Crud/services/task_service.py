from repositories.task_repository import TaskRepository
from schemas.task_schema import TaskCreate,TaskUpdate

class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def add_new_task(self, task_data: TaskCreate):
        # Business Logic Example: Capitalize the title before saving
        task_data.title = task_data.title.strip().capitalize()
        
        return self.repository.create_task(task_data)
    
    def get_task(self, task_id: int):
        task = self.repository.get_task_by_id(task_id)
        return task
    def delete_task(self, task_id: int):
        task = self.repository.delete_task_by_id(task_id)
        return task
    def edit_task(self, task_id: int, task_data:TaskUpdate):
        task = self.repository.edit_task_by_id(task_id, task_data)
        return task