from services.task_service import TaskService
from schemas.task_schema import TaskCreate,TaskUpdate

class TaskController:
    def __init__(self, service: TaskService):
        self.service = service

    def create_task(self, task_data: TaskCreate):
        # The controller just passes the data to the service layer
        return self.service.add_new_task(task_data)
    def get_task(self, task_id: int):
        return self.service.get_task(task_id)
    def delete_task(self, task_id: int):
        return self.service.delete_task(task_id)
    def edit_task(self, task_id: int, task_data: TaskUpdate):
        return self.service.edit_task(task_id, task_data)