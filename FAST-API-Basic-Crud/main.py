from fastapi import FastAPI
from routes import task_routes
from utils.database import engine, Base

# Create the database tables (Local only - in AWS you'd use Migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Management System")

# Include our routes
app.include_router(task_routes.router)

@app.get("/")
def health_check():
    return {"status": "online", "message": "Task API is running"}