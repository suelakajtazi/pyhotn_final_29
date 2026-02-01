"""
Database Manager - SQLite database operations using OOP
"""

import sqlite3
import hashlib
from datetime import datetime
from typing import Optional, List, Tuple


class Database:
    """Handles SQLite database connection and table creation."""
    
    def __init__(self, db_path: str = "reading_tracker.db"):
        self.db_path = db_path
        self.create_tables()
    
    def get_connection(self):
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_tables(self):
        """Create database tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                yearly_goal INTEGER DEFAULT 12,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Books table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                genre TEXT,
                total_pages INTEGER DEFAULT 0,
                current_page INTEGER DEFAULT 0,
                status TEXT DEFAULT 'to_read',
                rating REAL,
                review TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        conn.close()


class UserRepository:
    """Handles user database operations."""
    
    def __init__(self, database: Database):
        self.db = database
    
    def hash_password(self, password: str) -> str:
        """Create a simple hash of the password."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, email: str, password: str) -> Optional[int]:
        """Create a new user. Returns user ID or None if failed."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username.lower(), email.lower(), password_hash)
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    def login(self, username: str, password: str) -> Optional[dict]:
        """Check login credentials. Returns user data or None."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute(
            "SELECT id, username, email, yearly_goal FROM users WHERE username = ? AND password_hash = ?",
            (username.lower(), password_hash)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_user(self, user_id: int) -> Optional[dict]:
        """Get user by ID."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, username, email, yearly_goal FROM users WHERE id = ?",
            (user_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def update_yearly_goal(self, user_id: int, goal: int) -> bool:
        """Update user's yearly reading goal."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE users SET yearly_goal = ? WHERE id = ?",
            (goal, user_id)
        )
        
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated
    
    def username_exists(self, username: str) -> bool:
        """Check if username is already taken."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username.lower(),))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists


class BookRepository:
    """Handles book database operations."""
    
    def __init__(self, database: Database):
        self.db = database
    
    def add_book(self, user_id: int, title: str, author: str, 
                 genre: str = None, total_pages: int = 0, status: str = "to_read") -> int:
        """Add a new book. Returns book ID."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        started_at = datetime.now() if status == "reading" else None
        
        cursor.execute("""
            INSERT INTO books (user_id, title, author, genre, total_pages, status, started_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, title, author, genre, total_pages, status, started_at))
        
        conn.commit()
        book_id = cursor.lastrowid
        conn.close()
        return book_id
    
    def get_book(self, book_id: int) -> Optional[dict]:
        """Get a book by ID."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_user_books(self, user_id: int, status: str = None) -> List[dict]:
        """Get all books for a user. Can filter by status."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute(
                "SELECT * FROM books WHERE user_id = ? AND status = ? ORDER BY created_at DESC",
                (user_id, status)
            )
        else:
            cursor.execute(
                "SELECT * FROM books WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def update_status(self, book_id: int, status: str) -> bool:
        """Update book status."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now()
        
        if status == "reading":
            cursor.execute(
                "UPDATE books SET status = ?, started_at = COALESCE(started_at, ?) WHERE id = ?",
                (status, now, book_id)
            )
        elif status == "completed":
            cursor.execute(
                "UPDATE books SET status = ?, completed_at = ? WHERE id = ?",
                (status, now, book_id)
            )
        else:
            cursor.execute(
                "UPDATE books SET status = ? WHERE id = ?",
                (status, book_id)
            )
        
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated
    
    def update_progress(self, book_id: int, current_page: int) -> bool:
        """Update current reading page."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE books SET current_page = ? WHERE id = ?",
            (current_page, book_id)
        )
        
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated
    
    def rate_book(self, book_id: int, rating: float, review: str = None) -> bool:
        """Add rating and review to a book."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE books SET rating = ?, review = ? WHERE id = ?",
            (rating, review, book_id)
        )
        
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated
    
    def delete_book(self, book_id: int) -> bool:
        """Delete a book."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    
    def get_completed_count(self, user_id: int, year: int = None) -> int:
        """Count completed books for a user."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if year:
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            cursor.execute("""
                SELECT COUNT(*) as count FROM books 
                WHERE user_id = ? AND status = 'completed' 
                AND date(completed_at) BETWEEN date(?) AND date(?)
            """, (user_id, start_date, end_date))
        else:
            cursor.execute(
                "SELECT COUNT(*) as count FROM books WHERE user_id = ? AND status = 'completed'",
                (user_id,)
            )
        
        result = cursor.fetchone()
        count = result['count'] if result else 0
        conn.close()
        return count
    
    def get_most_read_author(self, user_id: int) -> Optional[Tuple[str, int]]:
        """Get the most read author for a user."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT author, COUNT(*) as count FROM books 
            WHERE user_id = ? AND status = 'completed'
            GROUP BY author ORDER BY count DESC LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return (row['author'], row['count'])
        return None
    
    def get_highest_rated(self, user_id: int) -> Optional[dict]:
        """Get the highest rated book for a user."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM books 
            WHERE user_id = ? AND rating IS NOT NULL
            ORDER BY rating DESC LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_trending_book(self) -> Optional[dict]:
        """Get the most popular book among all users."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT title, author, AVG(rating) as avg_rating, COUNT(*) as read_count
            FROM books 
            WHERE status = 'completed' AND rating IS NOT NULL
            GROUP BY title, author
            ORDER BY read_count DESC, avg_rating DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_stats(self, user_id: int) -> dict:
        """Get reading statistics for a user."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Count books by status
        cursor.execute("""
            SELECT status, COUNT(*) as count FROM books 
            WHERE user_id = ? GROUP BY status
        """, (user_id,))
        status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Average rating
        cursor.execute("""
            SELECT AVG(rating) as avg_rating FROM books 
            WHERE user_id = ? AND rating IS NOT NULL
        """, (user_id,))
        avg_rating = cursor.fetchone()['avg_rating'] or 0
        
        # Total pages read
        cursor.execute("""
            SELECT SUM(CASE WHEN status = 'completed' THEN total_pages ELSE current_page END) as total
            FROM books WHERE user_id = ?
        """, (user_id,))
        total_pages = cursor.fetchone()['total'] or 0
        
        # Books by genre
        cursor.execute("""
            SELECT genre, COUNT(*) as count FROM books 
            WHERE user_id = ? AND genre IS NOT NULL
            GROUP BY genre ORDER BY count DESC
        """, (user_id,))
        genres = {row['genre']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'to_read': status_counts.get('to_read', 0),
            'reading': status_counts.get('reading', 0),
            'completed': status_counts.get('completed', 0),
            'avg_rating': round(avg_rating, 1),
            'total_pages': total_pages,
            'genres': genres
        }
    
    def get_monthly_data(self, user_id: int, year: int) -> List[dict]:
        """Get monthly reading data for charts."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        
        cursor.execute("""
            SELECT strftime('%m', completed_at) as month, COUNT(*) as count
            FROM books 
            WHERE user_id = ? AND status = 'completed' 
            AND date(completed_at) BETWEEN date(?) AND date(?)
            GROUP BY strftime('%m', completed_at)
        """, (user_id, start_date, end_date))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
