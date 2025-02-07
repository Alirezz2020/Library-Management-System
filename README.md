# Library Management System

This is a **Library Management System** built with Django. It allows users to borrow and return books, while superusers (admins) can manage requests, track active borrows, and maintain the book collection.

## Features
- **User Authentication**: Users can sign up, log in, and borrow books.
- **Superuser Dashboard**: Admins can approve/reject borrow requests, track active borrows, and mark books as returned.
- **Book Management**: List of available books with pagination and search functionality.
- **Borrowing System**: Users can request books, and admins manage approval.
- **Pagination**: Implemented for book lists and borrow history.
- **Search Functionality**: Users can search for books by title or author.

## Setup Instructions

1. **Clone the repository**
   ```sh
   git clone https://github.com/Alirezz2020/Library-Management-System.git
   cd Library-Management-System (path)
   
   ```
2. **Create a virtual environment and activate it**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
4. **Apply migrations**
   ```sh
   python manage.py migrate
   ```
5. **Create a superuser** (to access the admin dashboard)
   ```sh
   python manage.py createsuperuser
   ```
   Follow the prompts to set up a username, email, and password.

6. **Run the development server**
   ```sh
   python manage.py runserver
   ```
7. **Access the application**
   - Visit `http://127.0.0.1:8000/` for the main site.
   - Visit `http://127.0.0.1:8000/admin/` to log in as a superuser.

## Contribution
I'm not a frontend developer, so if you're experienced with frontend design, feel free to contribute and improve the UI! PRs are welcome. 🚀

## License
This project is open-source under the MIT License.
