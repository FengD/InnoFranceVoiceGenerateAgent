import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.webapp_fastapi import router as webapp_router
from app.api_fastapi import router as api_router

# Create main FastAPI app
app = FastAPI(title="Qwen3-TTS Inno France", version="1.0.0")

# Enable CORS for browser usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webapp_router)
app.include_router(api_router, prefix="/api")

# Mount static files
base_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "static")), name="static")
