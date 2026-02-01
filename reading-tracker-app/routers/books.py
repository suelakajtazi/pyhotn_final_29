"""
Books Router - API endpoints for book operations
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from database import Database, BookRepository, UserRepository


router = APIRouter(prefix="/books", tags=["books"])

# Initialize database
db = Database()
book_repo = BookRepository(db)
user_repo = UserRepository(db)


# Request/Response Models

class BookCreate(BaseModel):
    user_id: int
    title: str
    author: str
    genre: Optional[str] = None
    total_pages: int = 0
    status: str = "to_read"


class BookUpdate(BaseModel):
    status: Optional[str] = None
    current_page: Optional[int] = None


class BookRating(BaseModel):
    rating: float
    review: Optional[str] = None


# Endpoints

@router.post("/")
def add_book(book: BookCreate):
    """Add a new book."""
    book_id = book_repo.add_book(
        book.user_id,
        book.title,
        book.author,
        book.genre,
        book.total_pages,
        book.status
    )
    return {"message": "Book added", "book_id": book_id}


@router.get("/user/{user_id}")
def get_user_books(user_id: int, status: Optional[str] = None):
    """Get all books for a user."""
    books = book_repo.get_user_books(user_id, status)
    return books


@router.get("/{book_id}")
def get_book(book_id: int):
    """Get a single book by ID."""
    book = book_repo.get_book(book_id)
    
    if book:
        return book
    raise HTTPException(status_code=404, detail="Book not found")


@router.put("/{book_id}/status")
def update_status(book_id: int, status: str):
    """Update book status."""
    if status not in ["to_read", "reading", "completed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    success = book_repo.update_status(book_id, status)
    
    if success:
        return {"message": "Status updated"}
    raise HTTPException(status_code=404, detail="Book not found")


@router.put("/{book_id}/progress")
def update_progress(book_id: int, current_page: int):
    """Update reading progress."""
    book = book_repo.get_book(book_id)
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if book['total_pages'] > 0:
        current_page = min(current_page, book['total_pages'])
    
    book_repo.update_progress(book_id, current_page)
    
    # Auto-complete if finished
    if book['total_pages'] > 0 and current_page >= book['total_pages']:
        book_repo.update_status(book_id, "completed")
        return {"message": "Progress updated", "completed": True}
    
    return {"message": "Progress updated", "completed": False}


@router.put("/{book_id}/rating")
def rate_book(book_id: int, data: BookRating):
    """Rate and review a book."""
    if data.rating < 1 or data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    success = book_repo.rate_book(book_id, data.rating, data.review)
    
    if success:
        return {"message": "Rating saved"}
    raise HTTPException(status_code=404, detail="Book not found")


@router.delete("/{book_id}")
def delete_book(book_id: int):
    """Delete a book."""
    success = book_repo.delete_book(book_id)
    
    if success:
        return {"message": "Book deleted"}
    raise HTTPException(status_code=404, detail="Book not found")


@router.get("/stats/{user_id}")
def get_stats(user_id: int):
    """Get reading statistics for a user."""
    return book_repo.get_stats(user_id)


@router.get("/stats/{user_id}/yearly")
def get_yearly_progress(user_id: int):
    """Get yearly reading goal progress."""
    user = user_repo.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    year = datetime.now().year
    completed = book_repo.get_completed_count(user_id, year)
    goal = user['yearly_goal']
    
    return {
        "goal": goal,
        "completed": completed,
        "remaining": max(0, goal - completed),
        "percentage": round((completed / goal) * 100, 1) if goal > 0 else 0
    }


@router.get("/trending/all")
def get_trending():
    """Get trending book among all users."""
    book = book_repo.get_trending_book()
    
    if book:
        return book
    return {"message": "No trending data yet"}


@router.get("/author/{user_id}/most-read")
def get_most_read_author(user_id: int):
    """Get most read author for a user."""
    result = book_repo.get_most_read_author(user_id)
    
    if result:
        return {"author": result[0], "count": result[1]}
    return {"message": "No data yet"}


@router.get("/rated/{user_id}/highest")
def get_highest_rated(user_id: int):
    """Get highest rated book for a user."""
    book = book_repo.get_highest_rated(user_id)
    
    if book:
        return book
    return {"message": "No rated books yet"}
