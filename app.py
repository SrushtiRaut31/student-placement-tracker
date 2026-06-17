# Student Placement Tracker - FastAPI Backend
# Author: Training Project (Migrated from Flask to FastAPI)
# Description: A web application for managing student placements and skills

from fastapi import FastAPI, Request, Depends, HTTPException, Response, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import os
import sqlite3
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from datetime import datetime, timedelta
from typing import Optional


# ============================================================================
# ENVIRONMENT VARIABLE LOADING
# ============================================================================

def load_dotenv_file():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        return
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


load_dotenv_file()

# ============================================================================
# FASTAPI APPLICATION SETUP
# ============================================================================

app = FastAPI(title="Student Placement Tracker", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Add url_for as a global in Jinja2 templates (mimics Flask's url_for)
# This wraps request.url_for so templates can use {{ url_for('dashboard') }}
templates.env.globals["url_for"] = lambda request, name, **params: str(request.url_for(name, **params))

# Session middleware for storing user session in cookies (encrypted)
SESSION_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your_secret_key_change_this_in_production')
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY, max_age=86400)  # 24 hours

# Import JWT library
import jwt

# JWT configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key_change_this_in_production')
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_HOURS = int(os.getenv('JWT_EXP_DELTA_HOURS', '24'))

# Database configuration
SQLITE_DATABASE = 'database.db'
DATABASE_URL = os.getenv('DATABASE_URL')
PG_SCHEMA = os.getenv('PG_SCHEMA', 'placement_tracker')

# ============================================================================
# DATABASE INITIALIZATION AND HELPER FUNCTIONS
# ============================================================================


def get_db_connection():
    """
    Create and return a PostgreSQL database connection.
    Uses DATABASE_URL from .env or environment variables.
    """
    if not DATABASE_URL:
        raise RuntimeError('DATABASE_URL is not configured. Set it in the .env file or environment.')

    conn = psycopg.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute(sql.SQL('SET search_path TO {}').format(sql.Identifier(PG_SCHEMA)))
    conn.commit()
    return conn


def get_db_cursor(conn):
    return conn.cursor(row_factory=dict_row)


def migrate_sqlite_to_postgres():
    """
    Migrate existing SQLite data to PostgreSQL if a local SQLite database exists.
    """
    if not os.path.exists(SQLITE_DATABASE):
        return

    sqlite_conn = sqlite3.connect(SQLITE_DATABASE)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    pg_conn = get_db_connection()
    pg_conn.autocommit = False
    pg_cursor = pg_conn.cursor()

    try:
        pg_cursor.execute(sql.SQL('SELECT COUNT(*) FROM {}.students').format(sql.Identifier(PG_SCHEMA)))
        if pg_cursor.fetchone()[0] > 0:
            pg_conn.commit()
            return

        sqlite_cur.execute('SELECT id, name, email, password, created_at FROM students')
        students = sqlite_cur.fetchall()
        for student in students:
            pg_cursor.execute(
                sql.SQL('INSERT INTO {}.students (id, name, email, password, created_at) VALUES (%s, %s, %s, %s, %s)').format(sql.Identifier(PG_SCHEMA)),
                (student['id'], student['name'], student['email'], student['password'], student['created_at'])
            )

        sqlite_cur.execute('SELECT id, student_id, skill_name, created_at FROM skills')
        skills = sqlite_cur.fetchall()
        for skill in skills:
            pg_cursor.execute(
                sql.SQL('INSERT INTO {}.skills (id, student_id, skill_name, created_at) VALUES (%s, %s, %s, %s)').format(sql.Identifier(PG_SCHEMA)),
                (skill['id'], skill['student_id'], skill['skill_name'], skill['created_at'])
            )

        sqlite_cur.execute('SELECT id, student_id, company_name, status, date_applied, created_at FROM applications')
        applications = sqlite_cur.fetchall()
        for application in applications:
            pg_cursor.execute(
                sql.SQL('INSERT INTO {}.applications (id, student_id, company_name, status, date_applied, created_at) VALUES (%s, %s, %s, %s, %s, %s)').format(sql.Identifier(PG_SCHEMA)),
                (application['id'], application['student_id'], application['company_name'], application['status'], application['date_applied'], application['created_at'])
            )

        for table_name in ['students', 'skills', 'applications']:
            sequence_name = sql.SQL("pg_get_serial_sequence(%s, 'id')")
            pg_cursor.execute(
                sql.SQL('SELECT setval({}, (SELECT COALESCE(MAX(id), 0) FROM {}.{}), true)').format(
                    sequence_name,
                    sql.Identifier(PG_SCHEMA),
                    sql.Identifier(table_name)
                ),
                (f'{PG_SCHEMA}.{table_name}',)
            )

        pg_conn.commit()
    except Exception:
        pg_conn.rollback()
        raise
    finally:
        sqlite_cur.close()
        sqlite_conn.close()
        pg_cursor.close()
        pg_conn.close()


def init_db():
    """
    Initialize PostgreSQL schema and tables if they don't exist.
    """
    if not DATABASE_URL:
        raise RuntimeError('DATABASE_URL is not configured. Set it in the .env file or environment.')

    conn = get_db_connection()
    conn.autocommit = True
    cursor = conn.cursor()

    # Create schema if needed
    cursor.execute(sql.SQL('CREATE SCHEMA IF NOT EXISTS {}').format(sql.Identifier(PG_SCHEMA)))

    # Create students table
    cursor.execute(sql.SQL('''
        CREATE TABLE IF NOT EXISTS {}.students (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''').format(sql.Identifier(PG_SCHEMA)))

    # Create skills table
    cursor.execute(sql.SQL('''
        CREATE TABLE IF NOT EXISTS {}.skills (
            id SERIAL PRIMARY KEY,
            student_id INTEGER NOT NULL REFERENCES {}.students(id) ON DELETE CASCADE,
            skill_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''').format(sql.Identifier(PG_SCHEMA), sql.Identifier(PG_SCHEMA)))

    # Create applications table
    cursor.execute(sql.SQL('''
        CREATE TABLE IF NOT EXISTS {}.applications (
            id SERIAL PRIMARY KEY,
            student_id INTEGER NOT NULL REFERENCES {}.students(id) ON DELETE CASCADE,
            company_name TEXT NOT NULL,
            status TEXT DEFAULT 'Applied',
            date_applied TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''').format(sql.Identifier(PG_SCHEMA), sql.Identifier(PG_SCHEMA)))

    cursor.close()
    conn.close()
    print('PostgreSQL database initialized successfully!')

    migrate_sqlite_to_postgres()


# ============================================================================
# AUTHENTICATION HELPERS
# ============================================================================


def generate_jwt_token(user_id: int) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXP_DELTA_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload.get('user_id')
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ============================================================================
# DEPENDENCY: Get current user from session (HTML routes)
# ============================================================================


def get_current_user_from_session(request: Request):
    """Extract user info from session for HTML template routes."""
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    if user_id is None:
        return None, None
    return user_id, user_name


def login_required_html(request: Request):
    """Dependency to protect HTML routes - redirects to login if not authenticated."""
    user_id, user_name = get_current_user_from_session(request)
    if user_id is None or user_name is None:
        raise HTTPException(status_code=303, detail="Authentication required")
    return user_id, user_name


def login_required_api(request: Request):
    """Dependency to protect API routes - uses JWT Bearer token."""
    auth_header = request.headers.get('Authorization', '')
    token = None
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ', 1)[1].strip()

    if not token:
        raise HTTPException(status_code=401, detail='Authentication token required')

    user_id = decode_jwt_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail='Invalid or expired token')

    return user_id


# ============================================================================
# HTML ROUTES
# ============================================================================


@app.get('/')
async def index(request: Request):
    """
    Home page route.
    Redirects to dashboard if user is logged in, otherwise to login page.
    """
    user_id = request.session.get('user_id')
    if user_id is not None:
        return RedirectResponse(url=request.url_for('dashboard'), status_code=302)
    return RedirectResponse(url=request.url_for('login'), status_code=302)


@app.get('/register', response_class=HTMLResponse)
async def register_form(request: Request):
    """
    User registration form display route.
    GET: Display registration form
    """
    return templates.TemplateResponse("register.html", {"request": request})


@app.post('/register', response_class=HTMLResponse)
async def register_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    """
    User registration form submission route.
    POST: Process registration form and create new user account
    """
    # Validation
    if not all([name, email, password, confirm_password]):
        return templates.TemplateResponse("register.html", {"request": request, "error": "All fields are required!"})

    if password != confirm_password:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Passwords do not match!"})

    if len(password) < 6:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Password must be at least 6 characters long!"})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute('SELECT id FROM students WHERE email = %s', (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return templates.TemplateResponse("register.html", {"request": request, "error": "Email already registered!"})

        # Insert new student into database
        cursor.execute(
            'INSERT INTO students (name, email, password) VALUES (%s, %s, %s)',
            (name, email, password)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return RedirectResponse(url=request.url_for('login'), status_code=302)

    except Exception as e:
        return templates.TemplateResponse("register.html", {"request": request, "error": f"Database error: {str(e)}"})


@app.get('/login', response_class=HTMLResponse)
async def login_form(request: Request):
    """
    User login form display route.
    GET: Display login form
    """
    return templates.TemplateResponse("login.html", {"request": request})


@app.post('/login', response_class=HTMLResponse)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """
    User login form submission route.
    POST: Authenticate user and create session
    """
    if not email or not password:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Email and password are required!"})

    try:
        conn = get_db_connection()
        cursor = conn.cursor(row_factory=dict_row)

        # Query database for matching email and password
        cursor.execute(
            'SELECT id, name FROM students WHERE email = %s AND password = %s',
            (email, password)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            # Create session for authenticated user
            request.session['user_id'] = user['id']
            request.session['user_name'] = user['name']
            return RedirectResponse(url=request.url_for('dashboard'), status_code=302)
        else:
            return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password!"})

    except Exception as e:
        return templates.TemplateResponse("login.html", {"request": request, "error": f"Database error: {str(e)}"})


@app.get('/logout')
async def logout(request: Request):
    """
    User logout route.
    Clears the session and redirects to login page.
    """
    request.session.clear()
    return RedirectResponse(url=request.url_for('login'), status_code=302)


@app.get('/dashboard', response_class=HTMLResponse)
async def dashboard(request: Request, search: Optional[str] = Query(None)):
    """
    Student dashboard route.
    Displays student information, skills, and placement applications.
    Accessible only to logged-in users.
    """
    # Check authentication
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    if user_id is None or user_name is None:
        return RedirectResponse(url=request.url_for('login'), status_code=302)

    search_query = search.strip() if search else ''

    try:
        conn = get_db_connection()
        cursor = conn.cursor(row_factory=dict_row)

        # Get student information
        cursor.execute('SELECT * FROM students WHERE id = %s', (user_id,))
        student = cursor.fetchone()

        # Get all skills for the student
        cursor.execute('SELECT * FROM skills WHERE student_id = %s', (user_id,))
        skills = cursor.fetchall()

        # Get all placement applications for the student, optionally filtered by search query
        if search_query:
            cursor.execute(
                'SELECT * FROM applications WHERE student_id = %s AND company_name LIKE %s',
                (user_id, f'%{search_query}%')
            )
        else:
            cursor.execute('SELECT * FROM applications WHERE student_id = %s', (user_id,))
        applications = cursor.fetchall()

        cursor.close()
        conn.close()

        total_skills = len(skills)
        total_applications = len(applications)
        interview_count = sum(1 for app in applications if app['status'] and app['status'].lower().startswith('interview'))
        selected_count = sum(1 for app in applications if app['status'] and app['status'].lower() == 'selected')

        statistics = {
            'total_skills': total_skills,
            'total_applications': total_applications,
            'interview_count': interview_count,
            'selected_count': selected_count,
        }

        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "student": student,
                "skills": skills,
                "applications": applications,
                "statistics": statistics,
                "search_query": search_query,
                "session": {"user_id": user_id, "user_name": user_name},
            }
        )

    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "error": f"Database error: {str(e)}"})


@app.get('/add_skill', response_class=HTMLResponse)
async def add_skill_form(request: Request):
    """
    Add skill form display route.
    GET: Display form to add skill
    """
    user_id = request.session.get('user_id')
    if user_id is None:
        return RedirectResponse(url=request.url_for('login'), status_code=302)
    return templates.TemplateResponse("add_skill.html", {"request": request})


@app.post('/add_skill', response_class=HTMLResponse)
async def add_skill_submit(
    request: Request,
    skill_name: str = Form(...)
):
    """
    Add skill form submission route.
    POST: Insert new skill into database
    """
    user_id = request.session.get('user_id')
    if user_id is None:
        return RedirectResponse(url=request.url_for('login'), status_code=302)

    if not skill_name:
        return templates.TemplateResponse("add_skill.html", {"request": request, "error": "Skill name is required!"})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert skill into database
        cursor.execute(
            'INSERT INTO skills (student_id, skill_name) VALUES (%s, %s)',
            (user_id, skill_name)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return RedirectResponse(url=request.url_for('dashboard'), status_code=302)

    except Exception as e:
        return templates.TemplateResponse("add_skill.html", {"request": request, "error": f"Database error: {str(e)}"})


@app.post('/delete_skill/{skill_id}')
async def delete_skill(request: Request, skill_id: int):
    """
    Delete skill route.
    Removes a skill from the student's skill list.
    Only the skill owner can delete their skill.
    """
    user_id = request.session.get('user_id')
    if user_id is None:
        return RedirectResponse(url=request.url_for('login'), status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor(row_factory=dict_row)

        # Verify that the skill belongs to the current user
        cursor.execute(
            'SELECT id FROM skills WHERE id = %s AND student_id = %s',
            (skill_id, user_id)
        )
        skill = cursor.fetchone()

        if not skill:
            cursor.close()
            conn.close()
            return JSONResponse(status_code=404, content={'error': 'Skill not found!'})

        # Delete the skill
        cursor.execute('DELETE FROM skills WHERE id = %s', (skill_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return RedirectResponse(url=request.url_for('dashboard'), status_code=302)

    except Exception as e:
        return JSONResponse(status_code=500, content={'error': f'Database error: {str(e)}'})


@app.get('/add_application', response_class=HTMLResponse)
async def add_application_form(request: Request):
    """
    Add placement application form display route.
    GET: Display form to add application
    """
    user_id = request.session.get('user_id')
    if user_id is None:
        return RedirectResponse(url=request.url_for('login'), status_code=302)
    return templates.TemplateResponse("add_application.html", {"request": request})


@app.post('/add_application', response_class=HTMLResponse)
async def add_application_submit(
    request: Request,
    company_name: str = Form(...),
    status: str = Form('Applied')
):
    """
    Add placement application form submission route.
    POST: Insert new application into database
    """
    user_id = request.session.get('user_id')
    if user_id is None:
        return RedirectResponse(url=request.url_for('login'), status_code=302)

    if not company_name:
        return templates.TemplateResponse("add_application.html", {"request": request, "error": "Company name is required!"})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert application into database
        cursor.execute(
            'INSERT INTO applications (student_id, company_name, status) VALUES (%s, %s, %s)',
            (user_id, company_name, status)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return RedirectResponse(url=request.url_for('dashboard'), status_code=302)

    except Exception as e:
        return templates.TemplateResponse("add_application.html", {"request": request, "error": f"Database error: {str(e)}"})


# ============================================================================
# API ROUTES
# ============================================================================


@app.post('/api/register')
async def api_register(request: Request):
    data = await request.json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not all([name, email, password, confirm_password]):
        return JSONResponse(status_code=400, content={'error': 'All fields are required!'})

    if password != confirm_password:
        return JSONResponse(status_code=400, content={'error': 'Passwords do not match!'})

    if len(password) < 6:
        return JSONResponse(status_code=400, content={'error': 'Password must be at least 6 characters long!'})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM students WHERE email = %s', (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return JSONResponse(status_code=400, content={'error': 'Email already registered!'})

        cursor.execute(
            'INSERT INTO students (name, email, password) VALUES (%s, %s, %s)',
            (name, email, password)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return JSONResponse(status_code=201, content={'message': 'Registration successful'})

    except Exception as e:
        return JSONResponse(status_code=500, content={'error': f'Database error: {str(e)}'})


@app.post('/api/login')
async def api_login(request: Request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return JSONResponse(status_code=400, content={'error': 'Email and password are required!'})

    try:
        conn = get_db_connection()
        cursor = conn.cursor(row_factory=dict_row)

        cursor.execute(
            'SELECT id, name FROM students WHERE email = %s AND password = %s',
            (email, password)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            token = generate_jwt_token(user['id'])
            return JSONResponse(status_code=200, content={
                'message': 'Login successful',
                'token': token,
                'user': {'id': user['id'], 'name': user['name']}
            })
        return JSONResponse(status_code=401, content={'error': 'Invalid email or password!'})

    except Exception as e:
        return JSONResponse(status_code=500, content={'error': f'Database error: {str(e)}'})


@app.get('/api/skills')
async def api_get_skills(request: Request, user_id: int = Depends(login_required_api)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(row_factory=dict_row)
        cursor.execute('SELECT * FROM skills WHERE student_id = %s', (user_id,))
        skills = cursor.fetchall()
        cursor.close()
        conn.close()

        return JSONResponse(status_code=200, content={'skills': [dict(skill) for skill in skills]})

    except Exception as e:
        return JSONResponse(status_code=500, content={'error': f'Database error: {str(e)}'})


@app.post('/api/skills')
async def api_add_skill(request: Request, user_id: int = Depends(login_required_api)):
    data = await request.json()
    skill_name = data.get('skill_name')

    if not skill_name:
        return JSONResponse(status_code=400, content={'error': 'Skill name is required!'})

    try:
        conn = get_db_connection()
        cursor = conn.cursor(row_factory=dict_row)
        cursor.execute(
            'INSERT INTO skills (student_id, skill_name) VALUES (%s, %s) RETURNING *',
            (user_id, skill_name)
        )
        skill = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        return JSONResponse(status_code=201, content={'message': 'Skill added', 'skill': dict(skill)})

    except Exception as e:
        return JSONResponse(status_code=500, content={'error': f'Database error: {str(e)}'})


@app.delete('/api/skills/{skill_id}')
async def api_delete_skill(request: Request, skill_id: int, user_id: int = Depends(login_required_api)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(row_factory=dict_row)
        cursor.execute(
            'SELECT id FROM skills WHERE id = %s AND student_id = %s',
            (skill_id, user_id)
        )
        skill = cursor.fetchone()

        if not skill:
            cursor.close()
            conn.close()
            return JSONResponse(status_code=404, content={'error': 'Skill not found!'})

        cursor.execute('DELETE FROM skills WHERE id = %s', (skill_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return JSONResponse(status_code=200, content={'message': 'Skill deleted'})

    except Exception as e:
        return JSONResponse(status_code=500, content={'error': f'Database error: {str(e)}'})


@app.get('/api/applications')
async def api_get_applications(
    request: Request,
    user_id: int = Depends(login_required_api),
    search: Optional[str] = Query(None)
):
    search_query = search.strip() if search else ''

    try:
        conn = get_db_connection()
        cursor = conn.cursor(row_factory=dict_row)

        if search_query:
            cursor.execute(
                'SELECT * FROM applications WHERE student_id = %s AND company_name LIKE %s',
                (user_id, f'%{search_query}%')
            )
        else:
            cursor.execute('SELECT * FROM applications WHERE student_id = %s', (user_id,))

        applications = cursor.fetchall()
        cursor.close()
        conn.close()

        return JSONResponse(status_code=200, content={'applications': [dict(app) for app in applications]})

    except Exception as e:
        return JSONResponse(status_code=500, content={'error': f'Database error: {str(e)}'})


@app.post('/api/applications')
async def api_add_application(request: Request, user_id: int = Depends(login_required_api)):
    data = await request.json()
    company_name = data.get('company_name')
    status = data.get('status', 'Applied')

    if not company_name:
        return JSONResponse(status_code=400, content={'error': 'Company name is required!'})

    try:
        conn = get_db_connection()
        cursor = conn.cursor(row_factory=dict_row)
        cursor.execute(
            'INSERT INTO applications (student_id, company_name, status) VALUES (%s, %s, %s) RETURNING *',
            (user_id, company_name, status)
        )
        application = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        return JSONResponse(status_code=201, content={'message': 'Application added', 'application': dict(application)})

    except Exception as e:
        return JSONResponse(status_code=500, content={'error': f'Database error: {str(e)}'})


@app.get('/api/student/{student_id}')
async def api_get_student(request: Request, student_id: int, user_id: int = Depends(login_required_api)):
    """
    API endpoint to get student information.
    Returns student data in JSON format.
    """
    # Ensure user can only access their own data
    if student_id != user_id:
        return JSONResponse(status_code=403, content={'error': 'Unauthorized'})

    try:
        conn = get_db_connection()
        cursor = conn.cursor(row_factory=dict_row)

        cursor.execute('SELECT id, name, email FROM students WHERE id = %s', (student_id,))
        student = cursor.fetchone()
        cursor.close()
        conn.close()

        if not student:
            return JSONResponse(status_code=404, content={'error': 'Student not found'})

        return JSONResponse(status_code=200, content=dict(student))

    except Exception as e:
        return JSONResponse(status_code=500, content={'error': f'Database error: {str(e)}'})


# ============================================================================
# ERROR HANDLERS
# ============================================================================


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors - page not found."""
    return templates.TemplateResponse("error.html", {"request": request, "error": "Page not found!"}, status_code=404)


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors - internal server error."""
    return templates.TemplateResponse("error.html", {"request": request, "error": "Internal server error!"}, status_code=500)


# ============================================================================
# MAIN APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    import uvicorn

    # Initialize database on first run
    init_db()

    # Run FastAPI development server
    uvicorn.run(app, host='127.0.0.1', port=5000)