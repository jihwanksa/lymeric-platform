"""FastAPI application for Research Assistant"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Lymeric Research Assistant API",
    description="AI-powered research assistant with Claude Skills",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check"""
    return {
        "name": "Lymeric Research Assistant API",
        "version": "0.1.0",
        "status": "running",
        "claude_api_configured": bool(os.getenv("ANTHROPIC_API_KEY"))
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "anthropic_api_key_set": bool(os.getenv("ANTHROPIC_API_KEY"))
    }

# TODO: Add WebSocket endpoint for chat
# TODO: Add Claude Skills integration
