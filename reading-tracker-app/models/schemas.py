"""
Pydantic Models - Simple data validation for the Reading Tracker
"""

from pydantic import BaseModel
from typing import Optional
from enum import Enum


class BookStatus(str, Enum):
    """Book reading status options."""
    TO_READ = "to_read"
    READING = "reading"
    COMPLETED = "completed"


# User Models

class UserCreate(BaseModel):
    """Data for creating a new user."""
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    """Data for user login."""
    username: str
    password: str


class User(BaseModel):
    """User data returned from database."""
    id: int
    username: str
    email: str
    yearly_goal: int = 12


class GoalUpdate(BaseModel):
    """Data for updating yearly reading goal."""
    goal: int


# Book Models

class BookCreate(BaseModel):
    """Data for adding a new book."""
    title: str
    author: str
    genre: Optional[str] = None
    total_pages: int = 0
    status: str = "to_read"


class BookCreateRequest(BaseModel):
    """Data for adding a new book via API (includes user_id)."""
    user_id: int
    title: str
    author: str
    genre: Optional[str] = None
    total_pages: int = 0
    status: str = "to_read"


class BookUpdate(BaseModel):
    """Data for updating a book."""
    status: Optional[str] = None
    current_page: Optional[int] = None


class Book(BaseModel):
    """Book data returned from database."""
    id: int
    user_id: int
    title: str
    author: str
    genre: Optional[str] = None
    total_pages: int = 0
    current_page: int = 0
    status: str = "to_read"
    rating: Optional[float] = None
    review: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def get_progress(self) -> float:
        """Calculate reading progress percentage."""
        if self.total_pages == 0:
            return 0.0
        return round((self.current_page / self.total_pages) * 100, 1)


class BookRating(BaseModel):
    """Data for rating a book."""
    rating: float
    review: Optional[str] = None


# Statistics Models

class DashboardStats(BaseModel):
    """Dashboard statistics data."""
    total_books: int = 0
    books_reading: int = 0
    books_completed: int = 0
    books_to_read: int = 0
    total_pages: int = 0
    avg_rating: float = 0.0
    genres: dict = {}


class YearlyProgress(BaseModel):
    """Yearly reading goal progress."""
    goal: int
    completed: int
    remaining: int
    percentage: float
