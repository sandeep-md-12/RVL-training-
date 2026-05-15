from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from utils.database import get_db
from repositories.task_repository import TaskRepository
from services.task_service import TaskService
from controllers.task_controller import TaskController
from schemas.task_schema import TaskCreate, TaskResponse,TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskResponse)
def create_task_endpoint(task_data: TaskCreate, db: Session = Depends(get_db)):
    # Manual Wiring for now (The "Lego" assembly)
    repo = TaskRepository(db)
    service = TaskService(repo)
    controller = TaskController(service)
    
    return controller.create_task(task_data)
from fastapi import HTTPException # Import this for errors

@router.get("/{task_id}", response_model=TaskResponse)
def get_task_endpoint(task_id: int, db: Session = Depends(get_db)):
    repo = TaskRepository(db)
    service = TaskService(repo)
    controller = TaskController(service)
    
    task = controller.get_task(task_id)
    
    # If the task doesn't exist or is_active is False
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def delete_task_endpoint(task_id: int, db: Session = Depends(get_db)):
    repo = TaskRepository(db)
    service = TaskService(repo)
    controller = TaskController(service)
    
    task = controller.delete_task(task_id)
    
    # If the task doesn't exist or is_active is False
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return task

@router.put("/edit/{task_id}", response_model=TaskResponse)
def edit_task_endpoint(task_id: int,task_data: TaskUpdate, db: Session = Depends(get_db)):
    repo = TaskRepository(db)
    service = TaskService(repo)
    controller = TaskController(service)
    
    task = controller.edit_task(task_id,task_data)
    
    # If the task doesn't exist or is_active is False
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return task