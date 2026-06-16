# Student Placement Tracker - Flask Backend

A comprehensive web application built with Python Flask for managing student placements, skills, and job applications. This backend provides a complete system for students to register, track their skills, and monitor their placement applications.

## Features

- **Student Authentication**: User registration and login with Flask sessions
- **Profile Management**: Store and manage student information
- **Skill Management**: Add, view, and delete technical skills
- **Placement Tracking**: Add and track placement applications with different statuses
- **Responsive Design**: Mobile-friendly interface using modern CSS
- **Database Integration**: SQLite database for data persistence
- **Security**: Session-based authentication with login required decorators

## Project Structure

```
training_project/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── database.db              # SQLite database (auto-created)
├── templates/               # HTML templates directory
│   ├── base.html           # Base template with navigation
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── dashboard.html      # Main dashboard
│   ├── add_skill.html      # Add skill form
│   ├── add_application.html # Add application form
│   └── error.html          # Error page
└── static/                  # Static files directory
    └── style.css           # Stylesheet
```

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## Installation & Setup

### Step 1: Clone or Navigate to Project Directory
```bash
cd path/to/training_project
```

### Step 2: Create a Virtual Environment (Optional but Recommended)

**For Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**For macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

## Usage

### First Time Access

1. **Register a New Account**
   - Navigate to `http://127.0.0.1:5000/register`
   - Enter your full name, email, and password
   - Password must be at least 6 characters long
   - Click "Register" button

2. **Login to Your Account**
   - Navigate to `http://127.0.0.1:5000/login`
   - Enter your registered email and password
   - Click "Login" button

3. **Access Dashboard**
   - After successful login, you'll be redirected to the dashboard
   - View your profile information, skills, and applications

### Managing Skills

- **Add Skill**: Click "+ Add Skill" button on dashboard
  - Enter skill name (e.g., Python, Java, React)
  - Click "Add Skill"

- **View Skills**: All your skills are displayed on the dashboard
  - Skills are shown as colored badges

- **Delete Skill**: Click "Delete" button next to any skill
  - Confirm deletion when prompted

### Managing Placement Applications

- **Add Application**: Click "+ Add Application" button on dashboard
  - Enter company name
  - Select application status (Applied, Under Review, Interview, Offer, Rejected)
  - Click "Add Application"

- **View Applications**: All applications are displayed in a table on dashboard
  - Shows company name, status, and date applied

- **Track Status**: Update applications by adding new entries with different statuses

### Logout

- Click "Logout" in the navigation bar to end your session
- You'll be redirected to the login page

## Database Schema

### students table
```sql
id (INTEGER PRIMARY KEY)
name (TEXT NOT NULL)
email (TEXT UNIQUE NOT NULL)
password (TEXT NOT NULL)
created_at (TIMESTAMP)
```

### skills table
```sql
id (INTEGER PRIMARY KEY)
student_id (INTEGER FOREIGN KEY)
skill_name (TEXT NOT NULL)
created_at (TIMESTAMP)
```

### applications table
```sql
id (INTEGER PRIMARY KEY)
student_id (INTEGER FOREIGN KEY)
company_name (TEXT NOT NULL)
status (TEXT DEFAULT 'Applied')
date_applied (TIMESTAMP)
created_at (TIMESTAMP)
```

## Routes

| Route | Method | Description | Auth Required |
|-------|--------|-------------|---|
| `/` | GET | Home page (redirects to login/dashboard) | No |
| `/register` | GET, POST | User registration | No |
| `/login` | GET, POST | User login | No |
| `/logout` | GET | User logout | Yes |
| `/dashboard` | GET | Main dashboard | Yes |
| `/add_skill` | GET, POST | Add new skill | Yes |
| `/delete_skill/<id>` | POST | Delete skill | Yes |
| `/add_application` | GET, POST | Add placement application | Yes |
| `/api/student/<id>` | GET | Get student info (JSON) | Yes |

## Code Structure

### Authentication
The application uses Flask sessions for authentication. The `@login_required` decorator ensures routes are only accessible to authenticated users.

### Database
SQLite is used for data persistence. Database connection is managed through the `get_db_connection()` function, and database initialization happens automatically on first run.

### Error Handling
Comprehensive error handling includes:
- Form validation
- Database error handling
- HTTP error handlers (404, 500)

## Security Considerations

⚠️ **Important**: This is a development version. For production use:

1. **Change Secret Key**: Update `app.secret_key` in app.py
   ```python
   app.secret_key = 'your-very-secure-random-key-here'
   ```

2. **Hash Passwords**: Implement password hashing using `werkzeug.security`:
   ```python
   from werkzeug.security import generate_password_hash, check_password_hash
   ```

3. **Use HTTPS**: Deploy with SSL/TLS certificates

4. **Database**: Use a production database like PostgreSQL instead of SQLite

5. **WSGI Server**: Use Gunicorn or uWSGI instead of Flask development server
   ```bash
   gunicorn -w 4 app:app
   ```

6. **Environment Variables**: Store sensitive data in environment variables

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify the port in app.py:
```python
app.run(debug=True, host='127.0.0.1', port=5001)
```

### Database Issues
If you encounter database issues, delete `database.db` and restart the application to reinitialize.

### Missing Templates
Ensure all template files are in the `templates/` directory with correct filenames.

### CSS Not Loading
Verify that the `style.css` file is in the `static/` directory and the static folder path is correct.

## Testing the Application

### Create Test Account
1. Go to `/register`
2. Fill in test details:
   - Name: John Doe
   - Email: john@example.com
   - Password: password123

### Test Features
1. Login with test account
2. Add 3-4 skills (Python, JavaScript, React, etc.)
3. Add 2-3 placement applications with different statuses
4. View dashboard to verify all data is displayed correctly
5. Delete a skill and verify it's removed
6. Logout and try to access dashboard (should redirect to login)

## Performance Notes

- SQLite is suitable for development and small deployments
- For large-scale deployments, migrate to PostgreSQL or MySQL
- Consider adding indexes on frequently queried columns
- Implement caching for better performance

## Future Enhancements

- Password hashing for security
- Email verification during registration
- Application status update functionality
- Interview scheduling system
- Resume upload functionality
- Admin dashboard for viewing all students
- Email notifications for application updates
- Two-factor authentication
- User profile pictures
- Search and filter functionality

## License

This project is for educational purposes. Feel free to modify and extend as needed.

## Support

For issues or questions:
1. Check the comments in app.py for code explanations
2. Review the error messages in the browser console
3. Check terminal output for Flask error logs
4. Verify database.db exists and has correct permissions

## Author

Training Project - 2024

---

**Happy Learning! 🚀**
