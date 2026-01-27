import os
import sys
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webapp_fastapi import app as webapp_router
from api_fastapi import app as api_router

# Create main FastAPI app
app = FastAPI(title="Qwen3-TTS Inno France", version="1.0.0")

# Include routers
app.include_router(webapp_router)
app.include_router(api_router, prefix="/api")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Qwen3-TTS Inno France API Server"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "qwen3-tts-inno-france"}