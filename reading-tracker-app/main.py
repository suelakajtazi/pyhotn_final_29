"""
Main FastAPI Application - Reading Tracker API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.users import router as users_router
from routers.books import router as books_router


# Create FastAPI app
app = FastAPI(
    title="Reading Tracker API",
    description="API for tracking your reading habits",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users_router)
app.include_router(books_router)


@app.get("/")
def root():
    """API root endpoint."""
    return {
        "message": "Welcome to Reading Tracker API",
        "docs": "/docs",
        "endpoints": {
            "users": "/users",
            "books": "/books"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Run with: uvicorn main:app --reload
