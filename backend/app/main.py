# backend/app/main.py
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any

from app.api.v1 import bug_analysis
from app.core.config import settings
# from app.database.database import init_db

# Application lifespan events for database initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up BugHawkAI Backend...")
    # Initialize database
    try:
        # init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        # Depending on criticality, you might want to exit or log more severely
    yield
    print("Shutting down BugHawkAI Backend...")

app = FastAPI(
    title="BugHawkAI Backend API",
    description="API for AI-powered log analysis, bug prediction, and patch suggestion for mobile apps.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for local development and eventual production origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production for specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(bug_analysis.router, prefix="/api/v1", tags=["Bug Analysis"])

@app.get("/")
async def root():
    return {"message": "Welcome to BugHawkAI API! Check /docs for API documentation."}

if __name__ == "__main__":
    import uvicorn
    # This block is for local development and testing.
    # In production, you'd typically run with `uvicorn app.main:app --host 0.0.0.0 --port 8000`
    uvicorn.run(app, host="0.0.0.0", port=8000)
