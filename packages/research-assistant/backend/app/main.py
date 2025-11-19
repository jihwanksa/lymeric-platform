"""Research Assistant Backend - Main FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys

# Add data-platform to path for shared database
sys.path.append('/Users/jihwan/Downloads/lymeric-platform/packages/data-platform/backend')
from app.core.database import engine, Base
from app.models.conversation import Conversation, Message

# Create conversation tables
Base.metadata.create_all(bind=engine)

# Import routers
from app.api import chat

app = FastAPI(
    title="Lymeric Research Assistant API",
    description="AI-powered research assistant for materials science",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/")
def root():
    return {
        "name": "Lymeric Research Assistant API",
        "version": "1.0.0",
        "status": "running",
        "mode": "mock"  # Indicates we're using mock Claude responses
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
