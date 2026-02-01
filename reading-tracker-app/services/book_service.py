"""
Service Layer - Business logic for the Reading Tracker
"""

from datetime import datetime
from typing import List, Optional, Tuple

from database import Database, UserRepository, BookRepository


class UserService:
    """Handles user-related business logic."""
    
    def __init__(self):
        self.db = Database()
        self.user_repo = UserRepository(self.db)
    
    def register(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        """Register a new user. Returns (success, message)."""
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        if "@" not in email:
            return False, "Please enter a valid email"
        
        if self.user_repo.username_exists(username):
            return False, "Username already taken"
        
        user_id = self.user_repo.create_user(username, email, password)
        
        if user_id:
            return True, "Account created successfully!"
        return False, "Registration failed. Please try again."
    
    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[dict]]:
        """Login a user. Returns (success, message, user_data)."""
        user = self.user_repo.login(username, password)
        
        if user:
            return True, "Welcome back!", user
        return False, "Invalid username or password", None
    
    def update_goal(self, user_id: int, goal: int) -> bool:
        """Update yearly reading goal."""
        if goal < 1 or goal > 100:
            return False
        return self.user_repo.update_yearly_goal(user_id, goal)


class BookService:
    """Handles book-related business logic."""
    
    def __init__(self):
        self.db = Database()
        self.book_repo = BookRepository(self.db)
    
    def add_book(self, user_id: int, title: str, author: str,
                 genre: str = None, total_pages: int = 0, status: str = "to_read") -> int:
        """Add a new book and return its ID."""
        return self.book_repo.add_book(user_id, title, author, genre, total_pages, status)
    
    def get_books(self, user_id: int, status: str = None) -> List[dict]:
        """Get all books for a user."""
        return self.book_repo.get_user_books(user_id, status)
    
    def update_status(self, book_id: int, status: str) -> bool:
        """Update book status."""
        return self.book_repo.update_status(book_id, status)
    
    def update_progress(self, book_id: int, page: int) -> bool:
        """Update reading progress. Returns success."""
        book = self.book_repo.get_book(book_id)
        if not book:
            return False
        
        if book['total_pages'] > 0:
            page = min(page, book['total_pages'])
        
        self.book_repo.update_progress(book_id, page)
        return True
    
    def rate_book(self, book_id: int, rating: float, review: str = None) -> bool:
        """Add rating and review."""
        return self.book_repo.rate_book(book_id, rating, review)
    
    def delete_book(self, book_id: int) -> bool:
        """Delete a book."""
        return self.book_repo.delete_book(book_id)


class StatsService:
    """Handles statistics and dashboard data."""
    
    def __init__(self):
        self.db = Database()
        self.book_repo = BookRepository(self.db)
        self.user_repo = UserRepository(self.db)
    
    def get_dashboard_stats(self, user_id: int) -> dict:
        """Get all statistics for the dashboard."""
        return self.book_repo.get_stats(user_id)
    
    def get_yearly_progress(self, user_id: int) -> dict:
        """Get yearly goal progress."""
        user = self.user_repo.get_user(user_id)
        if not user:
            return {"goal": 12, "completed": 0, "remaining": 12, "percentage": 0}
        
        year = datetime.now().year
        completed = self.book_repo.get_completed_count(user_id, year)
        goal = user['yearly_goal']
        
        return {
            "goal": goal,
            "completed": completed,
            "remaining": max(0, goal - completed),
            "percentage": round((completed / goal) * 100, 1) if goal > 0 else 0
        }
    
    def get_most_read_author(self, user_id: int) -> Optional[Tuple[str, int]]:
        """Get most read author."""
        return self.book_repo.get_most_read_author(user_id)
    
    def get_highest_rated(self, user_id: int) -> Optional[dict]:
        """Get highest rated book."""
        return self.book_repo.get_highest_rated(user_id)
    
    def get_trending(self) -> Optional[dict]:
        """Get trending book among all users."""
        return self.book_repo.get_trending_book()
    
    def get_monthly_data(self, user_id: int) -> List[dict]:
        """Get monthly reading data for charts."""
        year = datetime.now().year
        data = self.book_repo.get_monthly_data(user_id, year)
        
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        monthly_dict = {row['month']: row['count'] for row in data}
        
        result = []
        for i in range(1, 13):
            month_key = f"{i:02d}"
            result.append({
                "month": i,
                "month_name": month_names[i-1],
                "books_completed": monthly_dict.get(month_key, 0)
            })
        
        return result
