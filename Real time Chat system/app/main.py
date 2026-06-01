from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.utils.database import init_db
from app.utils.exceptions import (
    NotFoundError, AlreadyExistsError, ForbiddenError,
    RoomFullError, AlreadyMemberError, NotMemberError,
    InvalidCredentialsError, InactiveUserError, MessageDeletedError
)
from app.routes import auth_routes, user_routes, room_routes, message_routes, ws_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Real-Time Chat System", version="1.0.0", lifespan=lifespan)

# ── Exception Handlers ───────────────────────────────────────────────────────

@app.exception_handler(NotFoundError)
async def not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(AlreadyExistsError)
async def already_exists_handler(request, exc):
    return JSONResponse(status_code=409, content={"detail": str(exc)})

@app.exception_handler(ForbiddenError)
async def forbidden_handler(request, exc):
    return JSONResponse(status_code=403, content={"detail": str(exc)})

@app.exception_handler(RoomFullError)
async def room_full_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(AlreadyMemberError)
async def already_member_handler(request, exc):
    return JSONResponse(status_code=409, content={"detail": str(exc)})

@app.exception_handler(NotMemberError)
async def not_member_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request, exc):
    return JSONResponse(status_code=401, content={"detail": str(exc)})

@app.exception_handler(InactiveUserError)
async def inactive_user_handler(request, exc):
    return JSONResponse(status_code=403, content={"detail": str(exc)})

@app.exception_handler(MessageDeletedError)
async def message_deleted_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred"})

# ── Routers ──────────────────────────────────────────────────────────────────

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(room_routes.router)
app.include_router(message_routes.router)
app.include_router(ws_routes.router)

# ── Health Check ─────────────────────────────────────────────────────────────

@app.get("/")
async def health():
    return {"status": "ok"}

