"""
Users Router - API endpoints for user operations
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from database import Database, UserRepository


router = APIRouter(prefix="/users", tags=["users"])

# Initialize database
db = Database()
user_repo = UserRepository(db)


# Request/Response Models

class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    yearly_goal: int


class GoalUpdate(BaseModel):
    goal: int


# Endpoints

@router.post("/register")
def register(user: UserCreate):
    """Register a new user."""
    if len(user.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    if "@" not in user.email:
        raise HTTPException(status_code=400, detail="Invalid email")
    
    user_id = user_repo.create_user(user.username, user.email, user.password)
    
    if user_id:
        return {"message": "User created successfully", "user_id": user_id}
    raise HTTPException(status_code=400, detail="Username or email already exists")


@router.post("/login")
def login(user: UserLogin):
    """Login a user."""
    result = user_repo.login(user.username, user.password)
    
    if result:
        return {"message": "Login successful", "user": result}
    raise HTTPException(status_code=401, detail="Invalid username or password")


@router.get("/{user_id}")
def get_user(user_id: int):
    """Get user by ID."""
    user = user_repo.get_user(user_id)
    
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


@router.put("/{user_id}/goal")
def update_goal(user_id: int, data: GoalUpdate):
    """Update yearly reading goal."""
    if data.goal < 1 or data.goal > 100:
        raise HTTPException(status_code=400, detail="Goal must be between 1 and 100")
    
    success = user_repo.update_yearly_goal(user_id, data.goal)
    
    if success:
        return {"message": "Goal updated successfully"}
    raise HTTPException(status_code=404, detail="User not found")
