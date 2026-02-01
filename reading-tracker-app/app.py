"""
Reading Tracker - Streamlit Application
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from services.book_service import UserService, BookService, StatsService


class ReadingTrackerApp:
    """Main application class."""
    
    def __init__(self):
        self.user_service = UserService()
        self.book_service = BookService()
        self.stats_service = StatsService()
    
    def run(self):
        """Start the application."""
        st.set_page_config(
            page_title="Reading Tracker",
            page_icon="📚",
            layout="wide"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 1rem;
        }
        .stat-number { font-size: 2rem; font-weight: bold; }
        .stat-label { font-size: 0.9rem; opacity: 0.9; }
        .book-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            margin-bottom: 1rem;
        }
        .book-title { font-weight: bold; color: #1f2937; }
        .book-author { color: #6b7280; font-size: 0.9rem; }
        </style>
        """, unsafe_allow_html=True)
        
        # Session state
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'page' not in st.session_state:
            st.session_state.page = "dashboard"
        if 'completing_book' not in st.session_state:
            st.session_state.completing_book = None
        
        # Route
        if st.session_state.user is None:
            self.show_auth()
        else:
            self.show_main()
    
    def show_auth(self):
        """Show login/register page."""
        st.markdown("<h1 style='text-align:center;'>📚 Reading Tracker</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#6b7280;'>Track your reading journey</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            tab1, tab2 = st.tabs(["Login", "Register"])
            
            with tab1:
                with st.form("login_form"):
                    st.subheader("Welcome Back!")
                    username = st.text_input("Username", key="login_user")
                    password = st.text_input("Password", type="password", key="login_pass")
                    
                    if st.form_submit_button("Login", use_container_width=True):
                        if username and password:
                            success, msg, user = self.user_service.login(username, password)
                            if success:
                                st.session_state.user = user
                                st.rerun()
                            else:
                                st.error(msg)
                        else:
                            st.warning("Please fill all fields")
            
            with tab2:
                with st.form("register_form"):
                    st.subheader("Create Account")
                    username = st.text_input("Username", key="reg_user")
                    email = st.text_input("Email", key="reg_email")
                    password = st.text_input("Password", type="password", key="reg_pass")
                    confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
                    
                    if st.form_submit_button("Register", use_container_width=True):
                        if not all([username, email, password, confirm]):
                            st.warning("Please fill all fields")
                        elif password != confirm:
                            st.error("Passwords don't match")
                        else:
                            success, msg = self.user_service.register(username, email, password)
                            if success:
                                st.success(msg + " Please login.")
                            else:
                                st.error(msg)
    
    def show_review_dialog(self):
        """Show dialog to rate and review a book when marking as completed."""
        book = st.session_state.completing_book
        
        st.markdown("---")
        st.subheader(f"Rate & Review: {book['title']}")
        st.caption(f"by {book['author']}")
        
        with st.form("complete_book_form"):
            st.write("How would you rate this book?")
            rating = st.slider("Rating", 1.0, 5.0, 3.0, 0.5)
            
            st.write("Share your thoughts (optional)")
            review = st.text_area(
                "Your review",
                placeholder="What did you think about this book?",
                height=100
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("Save & Complete", use_container_width=True):
                    # Update status to completed with rating and review
                    self.book_service.update_status(book['id'], "completed")
                    self.book_service.rate_book(book['id'], rating, review if review else None)
                    st.session_state.completing_book = None
                    st.success(f"'{book['title']}' marked as completed!")
                    st.rerun()
            
            with col2:
                if st.form_submit_button("Skip Review", use_container_width=True):
                    # Just update status without review
                    self.book_service.update_status(book['id'], "completed")
                    st.session_state.completing_book = None
                    st.rerun()
        
        if st.button("Cancel"):
            st.session_state.completing_book = None
            st.rerun()
        
        st.markdown("---")
    
    def show_main(self):
        """Show main application."""
        self.show_sidebar()
        
        # Show review dialog if completing a book
        if st.session_state.completing_book:
            self.show_review_dialog()
            return
        
        page = st.session_state.page
        
        if page == "dashboard":
            self.show_dashboard()
        elif page == "my_books":
            self.show_my_books()
        elif page == "library":
            self.show_library()
        elif page == "add_book":
            self.show_add_book()
        elif page == "settings":
            self.show_settings()
    
    def show_sidebar(self):
        """Show navigation sidebar."""
        with st.sidebar:
            st.markdown(f"### 📚 Reading Tracker")
            st.markdown(f"Hello, **{st.session_state.user['username']}**!")
            st.markdown("---")
            
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.page = "dashboard"
                st.rerun()
            
            if st.button("📖 My Books", use_container_width=True):
                st.session_state.page = "my_books"
                st.rerun()
            
            if st.button("📚 Your Library", use_container_width=True):
                st.session_state.page = "library"
                st.rerun()
            
            if st.button("➕ Add Book", use_container_width=True):
                st.session_state.page = "add_book"
                st.rerun()
            
            if st.button("⚙️ Settings", use_container_width=True):
                st.session_state.page = "settings"
                st.rerun()
            
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.page = "dashboard"
                st.rerun()
    
    def show_dashboard(self):
        """Show dashboard page."""
        user_id = st.session_state.user['id']
        
        st.header("Dashboard")
        
        # Get data
        stats = self.stats_service.get_dashboard_stats(user_id)
        yearly = self.stats_service.get_yearly_progress(user_id)
        most_read = self.stats_service.get_most_read_author(user_id)
        highest_rated = self.stats_service.get_highest_rated(user_id)
        trending = self.stats_service.get_trending()
        
        # Stats cards
        total = stats['to_read'] + stats['reading'] + stats['completed']
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Books", total)
        col2.metric("Reading", stats['reading'])
        col3.metric("Completed", stats['completed'])
        col4.metric("Pages Read", f"{stats['total_pages']:,}")
        
        st.markdown("---")
        st.subheader("Reading Highlights")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if most_read:
                st.metric("Most-Read Author", most_read[0], f"{most_read[1]} books")
            else:
                st.metric("Most-Read Author", "---", "Complete books to see")
        
        with col2:
            if highest_rated:
                title = highest_rated['title'][:15] + "..." if len(highest_rated['title']) > 15 else highest_rated['title']
                st.metric("Highest Rated", title, f"★ {highest_rated['rating']}/5")
            else:
                st.metric("Highest Rated", "---", "Rate books to see")
        
        with col3:
            st.metric("Yearly Goal", f"{yearly['completed']}/{yearly['goal']}", f"{yearly['percentage']}% done")
        
        with col4:
            if trending:
                title = trending['title'][:15] + "..." if len(trending['title']) > 15 else trending['title']
                st.metric("Trending Book", title, f"{trending['read_count']} readers")
            else:
                st.metric("Trending Book", "---", "No data yet")
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            monthly_data = self.stats_service.get_monthly_data(user_id)
            fig = px.bar(
                monthly_data,
                x='month_name',
                y='books_completed',
                title='Monthly Reading Progress',
                labels={'month_name': 'Month', 'books_completed': 'Books'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=yearly['completed'],
                title={'text': "Yearly Goal Progress"},
                gauge={
                    'axis': {'range': [0, yearly['goal']]},
                    'bar': {'color': "#10B981"},
                    'steps': [
                        {'range': [0, yearly['goal'] * 0.5], 'color': "#FEE2E2"},
                        {'range': [yearly['goal'] * 0.5, yearly['goal'] * 0.8], 'color': "#FEF3C7"},
                        {'range': [yearly['goal'] * 0.8, yearly['goal']], 'color': "#D1FAE5"}
                    ]
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
    
    def show_my_books(self):
        """Show my books page."""
        user_id = st.session_state.user['id']
        
        st.header("My Books")
        
        tab1, tab2, tab3, tab4 = st.tabs(["All Books", "Currently Reading", "To Read", "Completed"])
        
        with tab1:
            self.show_book_list(user_id, None, "all")
        with tab2:
            self.show_book_list(user_id, "reading", "reading")
        with tab3:
            self.show_book_list(user_id, "to_read", "toread")
        with tab4:
            self.show_book_list(user_id, "completed", "completed")
    
    def show_book_list(self, user_id: int, status: str, tab_prefix: str):
        """Show list of books with unique keys per tab."""
        books = self.book_service.get_books(user_id, status)
        
        if not books:
            st.info("No books found. Add some books to get started!")
            return
        
        for book in books:
            # Create unique key using tab prefix and book id
            key_prefix = f"{tab_prefix}_{book['id']}"
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{book['title']}**")
                st.markdown(f"by {book['author']}")
                if book.get('genre'):
                    st.caption(book['genre'])
                
                # Progress bar for reading books
                if book['total_pages'] > 0:
                    progress = book['current_page'] / book['total_pages']
                    st.progress(progress)
                    st.caption(f"{book['current_page']}/{book['total_pages']} pages ({progress*100:.1f}%)")
            
            with col2:
                # Status dropdown (only if not completed)
                if book['status'] != "completed":
                    statuses = ["to_read", "reading", "completed"]
                    current_idx = statuses.index(book['status'])
                    
                    new_status = st.selectbox(
                        "Status",
                        statuses,
                        index=current_idx,
                        key=f"status_{key_prefix}",
                        label_visibility="collapsed"
                    )
                    
                    if new_status != book['status']:
                        if new_status == "completed":
                            # Show review dialog before marking as completed
                            st.session_state.completing_book = book
                            st.rerun()
                        else:
                            self.book_service.update_status(book['id'], new_status)
                            st.rerun()
                
                # Progress input for reading books
                if book['status'] == "reading" and book['total_pages'] > 0:
                    new_page = st.number_input(
                        "Page",
                        min_value=0,
                        max_value=book['total_pages'],
                        value=book['current_page'],
                        key=f"page_{key_prefix}"
                    )
                    
                    if st.button("Update", key=f"update_{key_prefix}"):
                        # Check if reaching last page
                        if new_page >= book['total_pages']:
                            # Update progress first, then show review dialog
                            self.book_service.update_progress(book['id'], new_page)
                            book['current_page'] = new_page
                            st.session_state.completing_book = book
                            st.rerun()
                        else:
                            self.book_service.update_progress(book['id'], new_page)
                            st.rerun()
                
                # Rating for completed books
                if book['status'] == "completed":
                    rating = st.slider(
                        "Rating",
                        1.0, 5.0,
                        float(book['rating']) if book['rating'] else 3.0,
                        0.5,
                        key=f"rating_{key_prefix}"
                    )
                    
                    review = st.text_area(
                        "Review",
                        value=book['review'] or "",
                        key=f"review_{key_prefix}",
                        height=80
                    )
                    
                    if st.button("Save", key=f"save_{key_prefix}"):
                        self.book_service.rate_book(book['id'], rating, review)
                        st.success("Saved!")
                        st.rerun()
                
                # Delete button
                if st.button("Delete", key=f"delete_{key_prefix}"):
                    self.book_service.delete_book(book['id'])
                    st.rerun()
            
            st.markdown("---")
    
    def show_library(self):
        """Show library page (completed books)."""
        user_id = st.session_state.user['id']
        
        st.header("Your Library")
        st.caption("All your completed books")
        
        books = self.book_service.get_books(user_id, "completed")
        
        if not books:
            st.info("Your library is empty. Complete some books!")
            return
        
        # Stats
        total = len(books)
        rated = [b for b in books if b['rating']]
        avg_rating = sum(b['rating'] for b in rated) / len(rated) if rated else 0
        total_pages = sum(b['total_pages'] for b in books)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Books Read", total)
        col2.metric("Average Rating", f"★ {avg_rating:.1f}")
        col3.metric("Total Pages", f"{total_pages:,}")
        
        st.markdown("---")
        
        # Display books in grid
        cols = st.columns(2)
        
        for i, book in enumerate(books):
            with cols[i % 2]:
                with st.container():
                    st.markdown(f"**{book['title']}**")
                    st.markdown(f"by {book['author']}")
                    
                    if book.get('genre'):
                        st.caption(book['genre'])
                    
                    if book['rating']:
                        stars = "★" * int(book['rating']) + "☆" * (5 - int(book['rating']))
                        st.markdown(f"{stars} ({book['rating']}/5)")
                    
                    if book.get('review'):
                        st.markdown(f"*\"{book['review']}\"*")
                    
                    st.caption(f"{book['total_pages']} pages")
                    st.markdown("---")
    
    def show_add_book(self):
        """Show add book page."""
        st.header("Add New Book")
        
        with st.form("add_book_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Book Title *")
                author = st.text_input("Author *")
                genre = st.selectbox(
                    "Genre",
                    ["", "Fiction", "Non-Fiction", "Mystery", "Sci-Fi", "Fantasy",
                     "Romance", "Thriller", "Biography", "Self-Help", "History", "Other"]
                )
            
            with col2:
                total_pages = st.number_input("Total Pages", min_value=0, value=0)
                status = st.selectbox(
                    "Status",
                    ["to_read", "reading", "completed"],
                    format_func=lambda x: x.replace('_', ' ').title()
                )
            
            if st.form_submit_button("Add Book", use_container_width=True):
                if not title or not author:
                    st.error("Please fill in title and author")
                else:
                    user_id = st.session_state.user['id']
                    self.book_service.add_book(
                        user_id, title, author,
                        genre if genre else None,
                        total_pages, status
                    )
                    st.success(f"'{title}' added!")
                    st.session_state.page = "my_books"
                    st.rerun()
    
    def show_settings(self):
        """Show settings page."""
        st.header("Settings")
        
        user = st.session_state.user
        
        st.subheader("Profile")
        st.write(f"**Username:** {user['username']}")
        st.write(f"**Email:** {user['email']}")
        
        st.markdown("---")
        
        st.subheader("Yearly Reading Goal")
        
        new_goal = st.number_input(
            "Books to read this year",
            min_value=1,
            max_value=100,
            value=user['yearly_goal']
        )
        
        if st.button("Update Goal"):
            if self.user_service.update_goal(user['id'], new_goal):
                st.session_state.user['yearly_goal'] = new_goal
                st.success("Goal updated!")
            else:
                st.error("Failed to update goal")


# Run the app
if __name__ == "__main__":
    app = ReadingTrackerApp()
    app.run()
