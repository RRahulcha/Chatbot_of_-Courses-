import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

from app.database.database import engine, Base
from app.api import chat, enquiry, admin

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SETTribe AI Assistant API",
    description="Backend API for the SETTribe Student & Career Assistant",
    version="1.0.0",
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(",") if settings.allowed_origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(enquiry.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to SETTribe AI Assistant API"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
