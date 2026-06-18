# Student Placement Tracker - FastAPI Backend (Entry Point)
# Author: Training Project (Migrated from Flask to FastAPI)

from fastapi import FastAPI, Request, Depends, HTTPException, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from typing import Optional

from database import get_db_connection, get_db_cursor, init_db
from schemas import (
    UserRegister, UserLogin, SkillCreate, ApplicationCreate,
    UserResponse, TokenResponse, SkillResponse, ApplicationResponse, ErrorResponse
)
from auth import (
    generate_jwt_token, decode_jwt_token,
    login_required_api, get_current_user_from_session,
    security_scheme
)
from psycopg.rows import dict_row
import psycopg
import os

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

app = FastAPI(
    title="Student Placement Tracker API",
    description="A FastAPI-based backend for managing student placements, skills, and applications.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Expose url_for to templates via request object (matches Flask-style usage)
templates.env.globals["url_for"] = lambda request, name, **params: str(
    request.url_for(name, **params)
)

# Custom Jinja2 filter to safely format datetime objects (handles both string and datetime)
from datetime import datetime, date
def jinja_date_format(value, fmt="%Y-%m-%d"):
    if value is None:
        return "N/A"
    if hasattr(value, "strftime"):
        return value.strftime(fmt)
    if isinstance(value, str):
        return value.split(" ")[0]
    return str(value).split(" ")[0]

templates.env.filters["date_format"] = jinja_date_format

# Session middleware for encrypted cookie-based sessions
SESSION_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your_secret_key_change_this_in_production')
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY, max_age=86400)  # 24 hours

# ============================================================================
# HTML ROUTES (Frontend Pages)
# ============================================================================


@app.get('/', include_in_schema=False)
async def index(request: Request):
    """Home page. Redirects to dashboard if logged in, otherwise to login."""
    user_id = request.session.get('user_id')
    if user_id is not None:
        return RedirectResponse(url=request.url_for('dashboard'), status_code=302)
    return RedirectResponse(url=request.url_for('login_form'), status_code=302)


@app.get('/register', response_class=HTMLResponse, include_in_schema=False)
async def register_form(request: Request):
    """Display registration form."""
    return templates.TemplateResponse("register.html", {"request": request})


@app.post('/register', response_class=HTMLResponse, include_in_schema=False)
async def register_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Process registration form submission."""
    # Validation
    if not all([name, email, password, confirm_password]):
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "All fields are required!"}
        )
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "Passwords do not match!"}
        )
    if len(password) < 6:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "Password must be at least 6 characters long!"}
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute('SELECT id FROM students WHERE email = %s', (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return templates.TemplateResponse(
                "register.html", {"request": request, "error": "Email already registered!"}
            )

        # Insert new student
        cursor.execute(
            'INSERT INTO students (name, email, password) VALUES (%s, %s, %s)',
            (name, email, password)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return RedirectResponse(url=request.url_for('login_form'), status_code=302)

    except Exception as e:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": f"Database error: {str(e)}"}
        )


@app.get('/login', response_class=HTMLResponse, include_in_schema=False)
async def login_form(request: Request):
    """Display login form."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post('/login', response_class=HTMLResponse, include_in_schema=False)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """Process login form submission."""
    if not email or not password:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Email and password are required!"}
        )

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
            request.session['user_id'] = user['id']
            request.session['user_name'] = user['name']
            return RedirectResponse(url=request.url_for('dashboard'), status_code=302)
        else:
            return templates.TemplateResponse(
                "login.html", {"request": request, "error": "Invalid email or password!"}
            )

    except Exception as e:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": f"Database error: {str(e)}"}
        )


@app.get('/logout', include_in_schema=False)
async def logout(request: Request):
    """Logout user and clear session."""
    request.session.clear()
    return RedirectResponse(url=request.url_for('login_form'), status_code=302)


@app.get('/dashboard', response_class=HTMLResponse, include_in_schema=False)
async def dashboard(
    request: Request,
    search: Optional[str] = Query(None)
):
    """Student dashboard showing profile, skills, and applications."""
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    if user_id is None or user_name is None:
        return RedirectResponse(url=request.url_for('login_form'), status_code=302)

    search_query = search.strip() if search else ''

    try:
        conn = get_db_connection()
        cursor = conn.cursor(row_factory=dict_row)

        # Get student information
        cursor.execute('SELECT * FROM students WHERE id = %s', (user_id,))
        student = cursor.fetchone()

        # Get skills
        cursor.execute('SELECT * FROM skills WHERE student_id = %s', (user_id,))
        skills = cursor.fetchall()

        # Get applications (filtered by search if provided)
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

        # Calculate statistics
        total_skills = len(skills)
        total_applications = len(applications)
        interview_count = sum(
            1 for app in applications
            if app['status'] and app['status'].lower().startswith('interview')
        )
        selected_count = sum(
            1 for app in applications
            if app['status'] and app['status'].lower() == 'selected'
        )

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
        return templates.TemplateResponse(
            "error.html", {"request": request, "error": f"Database error: {str(e)}"}
        )


@app.get('/add_skill', response_class=HTMLResponse, include_in_schema=False)
async def add_skill_form(request: Request):
    """Display add skill form."""
    user_id = request.session.get('user_id')
    if user_id is None:
        return RedirectResponse(url=request.url_for('login_form'), status_code=302)
    return templates.TemplateResponse("add_skill.html", {"request": request})


@app.post('/add_skill', response_class=HTMLResponse, include_in_schema=False)
async def add_skill_submit(
    request: Request,
    skill_name: str = Form(...)
):
    """Process add skill form submission."""
    user_id = request.session.get('user_id')
    if user_id is None:
        return RedirectResponse(url=request.url_for('login_form'), status_code=302)

    if not skill_name:
        return templates.TemplateResponse(
            "add_skill.html", {"request": request, "error": "Skill name is required!"}
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO skills (student_id, skill_name) VALUES (%s, %s)',
            (user_id, skill_name)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return RedirectResponse(url=request.url_for('dashboard'), status_code=302)

    except Exception as e:
        return templates.TemplateResponse(
            "add_skill.html", {"request": request, "error": f"Database error: {str(e)}"}
        )


@app.post('/delete_skill/{skill_id}', include_in_schema=False)
async def delete_skill(request: Request, skill_id: int):
    """Delete a skill belonging to the current user."""
    user_id = request.session.get('user_id')
    if user_id is None:
        return RedirectResponse(url=request.url_for('login_form'), status_code=302)

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

        return RedirectResponse(url=request.url_for('dashboard'), status_code=302)

    except Exception as e:
        return JSONResponse(status_code=500, content={'error': f'Database error: {str(e)}'})


@app.get('/add_application', response_class=HTMLResponse, include_in_schema=False)
async def add_application_form(request: Request):
    """Display add application form."""
    user_id = request.session.get('user_id')
    if user_id is None:
        return RedirectResponse(url=request.url_for('login_form'), status_code=302)
    return templates.TemplateResponse("add_application.html", {"request": request})


@app.post('/add_application', response_class=HTMLResponse, include_in_schema=False)
async def add_application_submit(
    request: Request,
    company_name: str = Form(...),
    status: str = Form('Applied')
):
    """Process add application form submission."""
    user_id = request.session.get('user_id')
    if user_id is None:
        return RedirectResponse(url=request.url_for('login_form'), status_code=302)

    if not company_name:
        return templates.TemplateResponse(
            "add_application.html", {"request": request, "error": "Company name is required!"}
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO applications (student_id, company_name, status) VALUES (%s, %s, %s)',
            (user_id, company_name, status)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return RedirectResponse(url=request.url_for('dashboard'), status_code=302)

    except Exception as e:
        return templates.TemplateResponse(
            "add_application.html", {"request": request, "error": f"Database error: {str(e)}"}
        )


# ============================================================================
# API ROUTES (RESTful JSON Endpoints)
# ============================================================================


@app.post('/api/register', response_model=dict, tags=["Authentication"])
async def api_register(payload: UserRegister):
    """Register a new student account."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute('SELECT id FROM students WHERE email = %s', (payload.email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail='Email already registered!')

        # Insert new student
        cursor.execute(
            'INSERT INTO students (name, email, password) VALUES (%s, %s, %s)',
            (payload.name, payload.email, payload.password)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Registration successful"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')


@app.post('/api/login', response_model=TokenResponse, tags=["Authentication"])
async def api_login(payload: UserLogin):
    """Authenticate a student and return a JWT token."""
    if not payload.email or not payload.password:
        raise HTTPException(status_code=400, detail='Email and password are required!')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(row_factory=dict_row)

        cursor.execute(
            'SELECT id, name FROM students WHERE email = %s AND password = %s',
            (payload.email, payload.password)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            raise HTTPException(status_code=401, detail='Invalid email or password!')

        token = generate_jwt_token(user['id'])
        return TokenResponse(
            message="Login successful",
            token=token,
            user=UserResponse(id=user['id'], name=user['name'])
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')


@app.get('/api/skills', response_model=dict, tags=["Skills"])
async def api_get_skills(user_id: int = Depends(login_required_api)):
    """Get all skills for the authenticated student."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(row_factory=dict_row)
        cursor.execute('SELECT * FROM skills WHERE student_id = %s', (user_id,))
        skills = cursor.fetchall()
        cursor.close()
        conn.close()

        return {"skills": [dict(skill) for skill in skills]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')


@app.post('/api/skills', response_model=dict, tags=["Skills"])
async def api_add_skill(
    payload: SkillCreate,
    user_id: int = Depends(login_required_api)
):
    """Add a new skill for the authenticated student."""
    if not payload.skill_name:
        raise HTTPException(status_code=400, detail='Skill name is required!')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(row_factory=dict_row)
        cursor.execute(
            'INSERT INTO skills (student_id, skill_name) VALUES (%s, %s) RETURNING *',
            (user_id, payload.skill_name)
        )
        skill = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Skill added", "skill": dict(skill)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')


@app.delete('/api/skills/{skill_id}', response_model=dict, tags=["Skills"])
async def api_delete_skill(
    skill_id: int,
    user_id: int = Depends(login_required_api)
):
    """Delete a skill by ID (must belong to the authenticated student)."""
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
            raise HTTPException(status_code=404, detail='Skill not found!')

        cursor.execute('DELETE FROM skills WHERE id = %s', (skill_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Skill deleted"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')


@app.get('/api/applications', response_model=dict, tags=["Applications"])
async def api_get_applications(
    search: Optional[str] = Query(None),
    user_id: int = Depends(login_required_api)
):
    """Get all applications for the authenticated student. Optionally filter by company name."""
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

        return {"applications": [dict(app) for app in applications]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')


@app.post('/api/applications', response_model=dict, tags=["Applications"])
async def api_add_application(
    payload: ApplicationCreate,
    user_id: int = Depends(login_required_api)
):
    """Add a new placement application."""
    if not payload.company_name:
        raise HTTPException(status_code=400, detail='Company name is required!')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(row_factory=dict_row)
        cursor.execute(
            'INSERT INTO applications (student_id, company_name, status) VALUES (%s, %s, %s) RETURNING *',
            (user_id, payload.company_name, payload.status)
        )
        application = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Application added", "application": dict(application)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')


@app.get('/api/student/{student_id}', response_model=dict, tags=["Students"])
async def api_get_student(
    student_id: int,
    user_id: int = Depends(login_required_api)
):
    """Get student profile information. Only accessible for own profile."""
    if student_id != user_id:
        raise HTTPException(status_code=403, detail='Unauthorized')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(row_factory=dict_row)

        cursor.execute('SELECT id, name, email FROM students WHERE id = %s', (student_id,))
        student = cursor.fetchone()
        cursor.close()
        conn.close()

        if not student:
            raise HTTPException(status_code=404, detail='Student not found')

        return dict(student)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')


# ============================================================================
# OPENAPI SECURITY SCHEME (Swagger "Authorize" button)
# ============================================================================


def custom_openapi():
    """Register Bearer token security scheme in OpenAPI so Swagger shows Authorize button."""
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title="Student Placement Tracker API",
        version="1.0.0",
        description="A FastAPI-based backend for managing student placements, skills, and applications.",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# ============================================================================
# ERROR HANDLERS
# ============================================================================


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors - page not found."""
    # If it's an API request, return JSON
    if request.url.path.startswith('/api/'):
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    return templates.TemplateResponse(
        "error.html", {"request": request, "error": "Page not found!"}, status_code=404
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors - internal server error."""
    if request.url.path.startswith('/api/'):
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    return templates.TemplateResponse(
        "error.html", {"request": request, "error": "Internal server error!"}, status_code=500
    )


# ============================================================================
# MAIN APPLICATION ENTRY POINT
# ============================================================================


if __name__ == '__main__':
    # Initialize database before starting the server
    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        print("The application may not work correctly without a database connection.")

    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)