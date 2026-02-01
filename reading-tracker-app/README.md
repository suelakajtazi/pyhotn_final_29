# Reading Tracker Application

A web-based application designed to help users track, organize, and reflect on their reading habits.

## Features

- **User Authentication**: Register and login to keep your reading data private
- **Book Management**: Add books with title, author, genre, and page count
- **Reading Status**: Track books as "To Read", "Currently Reading", or "Completed"
- **Progress Tracking**: Update your current page as you read
- **Ratings & Reviews**: Rate completed books (1-5 stars) and write personal reviews
- **Personal Library**: View all completed books with ratings and reviews
- **Dashboard Analytics**:
  - Most-read author (based on completed books)
  - Highest-rated book (your favorite read)
  - Yearly reading goal progress
  - Trending book (most popular among all users)
  - Monthly reading charts
- **Yearly Goals**: Set and track your annual reading goals

## Technologies Used

- **Python 3.12+**
- **Streamlit**: Web interface and frontend
- **FastAPI**: REST API backend
- **SQLite**: Database storage
- **Plotly**: Interactive charts and visualizations
- **Pydantic**: Data validation

## Project Structure

```
reading-tracker/
├── app.py                 # Main Streamlit application
├── main.py                # FastAPI backend server
├── database.py            # SQLite database operations (OOP)
├── requirements.txt       # Python dependencies
├── models/
│   ├── __init__.py
│   └── schemas.py         # Pydantic data models
├── services/
│   ├── __init__.py
│   └── book_service.py    # Business logic layer
└── routers/
    ├── __init__.py
    ├── users.py           # User API endpoints
    └── books.py           # Book API endpoints
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd reading-tracker
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Streamlit Frontend (Main Application)
```bash
streamlit run app.py
```
The application will open in your browser at `http://localhost:8501`

### FastAPI Backend (Optional - for API access)
```bash
uvicorn main:app --reload
```
API documentation available at `http://localhost:8000/docs`

## Usage

1. **Register**: Create a new account with username, email, and password
2. **Login**: Access your personal reading tracker
3. **Add Books**: Click "Add Book" to add books to your collection
4. **Track Progress**: Update your current page as you read
5. **Complete Books**: When finished, rate and review your books
6. **View Library**: See all completed books in "Your Library"
7. **Dashboard**: Monitor your reading statistics and progress

## Database Schema

### Users Table
- id, username, email, password_hash, yearly_goal, created_at

### Books Table
- id, user_id, title, author, genre, total_pages, current_page
- status, rating, review, started_at, completed_at, created_at

## API Endpoints

### Users
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - Login user
- `GET /api/users/{user_id}` - Get user profile
- `PUT /api/users/{user_id}/goal` - Update yearly goal

### Books
- `GET /api/books/{user_id}` - Get user's books
- `POST /api/books/` - Add new book
- `PUT /api/books/{book_id}/status` - Update book status
- `PUT /api/books/{book_id}/progress` - Update reading progress
- `PUT /api/books/{book_id}/rating` - Add rating and review
- `DELETE /api/books/{book_id}` - Delete book

### Statistics
- `GET /api/stats/{user_id}` - Get user statistics
- `GET /api/stats/{user_id}/yearly` - Get yearly progress
- `GET /api/stats/trending` - Get trending book

## License

This project is for educational purposes.
