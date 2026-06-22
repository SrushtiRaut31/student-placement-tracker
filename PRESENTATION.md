# Student Placement Tracker - Project Presentation

---

## Slide 1: Introduction & Problem Statement

### Slide Title
Introduction & Problem Statement

### PPT Content
**What is the Student Placement Tracker?**
- A web-based application for managing student placement activities
- Tracks skills, job applications, and placement status in one place
- Migrated from Flask to FastAPI for better performance and async support

**Problem Statement:**
- Students struggle to maintain records of skills and job applications across multiple platforms
- No centralized system to track placement journey (Applied → Interview → Selected/Rejected)
- Manual tracking leads to missed opportunities and disorganized data
- Need for a simple, accessible platform to manage placement-related information

**Key Insight:**
- "A single student may apply to 20+ companies with varying skills — tracking this manually is error-prone and time-consuming."

### Speaker Notes (30-60 seconds)
"Good morning/afternoon. The Student Placement Tracker is a web application designed to solve a common problem faced by final-year students — managing placement activities. Currently, students apply to multiple companies through different portals and track their skills in spreadsheets or notes. This leads to disorganized data and missed opportunities. Our project provides a centralized platform where students can register, log in, manage their skills, and track every placement application with its current status — all in one place. We built this using FastAPI, a modern Python web framework, and deployed it on Render with a Neon PostgreSQL database."

### Suggested Screenshot/Diagram
- Screenshot of the Login page (`templates/login.html`) showing the clean, simple interface
- OR a problem-solution diagram showing "Manual Tracking → Centralized System"

### Viva Questions & Answers
**Q1: Why did you choose FastAPI over Flask?**
A: FastAPI offers automatic API documentation with Swagger UI, built-in data validation with Pydantic, async support for better performance, and type hints that reduce bugs. It's also faster than Flask for production deployments.

**Q2: What is the main problem your project solves?**
A: It solves the problem of students having to manually track their skills and job applications across multiple platforms. Everything is centralized in one dashboard.

**Q3: Who are the users of this system?**
A: The primary users are final-year engineering students who are actively looking for placements and need to track their skills and applications.

---

## Slide 2: Project Objectives & Scope

### Slide Title
Project Objectives & Scope

### PPT Content
**Primary Objectives:**
1. Provide a secure user registration and login system
2. Allow students to add, view, and delete skills
3. Enable tracking of placement applications with status updates
4. Offer a dashboard with real-time statistics
5. Support search functionality for applications
6. Provide both HTML (Jinja2) and REST API interfaces

**Project Scope:**
- **In Scope:**
  - Student registration and authentication
  - Skills management (CRUD operations)
  - Application tracking with status (Applied, Interview Scheduled, Selected, Rejected)
  - Dashboard with statistics (Total Skills, Applications, Interviews, Selected)
  - Search/filter applications by company name
  - REST API with JWT authentication
  - PostgreSQL database with proper relationships

- **Out of Scope:**
  - Admin panel for college placement officers
  - Resume upload and parsing
  - Company-wise job posting feed
  - Email notifications
  - Multi-user role management (only student role)

**Success Criteria:**
- User can register and login securely
- Dashboard loads with accurate statistics
- Skills and applications can be added/deleted
- Search works correctly across applications

### Speaker Notes (30-60 seconds)
"The main objectives of this project are to provide a secure, easy-to-use platform for students to manage their placement data. We focused on three core features: user authentication, skills management, and application tracking. The scope includes both a web interface using Jinja2 templates and a REST API with JWT authentication for future mobile app integration. We intentionally kept the scope focused — no admin panel, no resume uploads, no email notifications — to ensure we deliver a solid, working core system. The success criteria are straightforward: a student should be able to register, log in, add skills, track applications, and see meaningful statistics on their dashboard."

### Suggested Screenshot/Diagram
- Feature list diagram or a scope triangle diagram (In Scope / Out of Scope)
- Screenshot of the Dashboard showing statistics cards

### Viva Questions & Answers
**Q1: Why did you limit the scope to only student features?**
A: To ensure a focused, well-tested core functionality. Adding admin panels or company features would increase complexity and risk without adding value to the primary user — the student.

**Q2: What technologies did you consider before finalizing FastAPI?**
A: We considered Flask (the original version used Flask), Django, and Node.js with Express. FastAPI was chosen for its modern async support, automatic docs, and type safety.

**Q3: How do you measure the success of this project?**
A: Success is measured by functional completeness: can a user register, login, manage skills, track applications, and view statistics? All these must work correctly.

---

## Slide 3: Proposed System Overview

### Slide Title
Proposed System Overview

### PPT Content
**System Description:**
The Student Placement Tracker is a full-stack web application with:
- **Frontend:** Jinja2 templates with HTML/CSS/JavaScript
- **Backend:** FastAPI (Python) with async route handlers
- **Database:** PostgreSQL (Neon) with schema `placement_tracker`
- **Deployment:** Render cloud platform

**Core Modules:**
1. **Authentication Module** — Registration, Login, Session Management, JWT tokens
2. **Dashboard Module** — Statistics, Profile view, Skills list, Applications table
3. **Skills Module** — Add skill, Delete skill, View all skills
4. **Applications Module** — Add application, Search applications, Status tracking
5. **API Module** — REST endpoints for mobile/future integration

**User Flow:**
```
Register → Login → Dashboard → Add Skills → Add Applications → Search/Track
```

**Key Features:**
- Dual authentication: Session-based (HTML) + JWT-based (API)
- Real-time statistics calculation on dashboard
- Search/filter applications by company name
- Responsive design with CSS styling
- Error handling with custom error pages

### Speaker Notes (30-60 seconds)
"Our proposed system is a three-tier web application. The user interacts with the frontend — Jinja2 templates rendered by FastAPI. The backend handles all business logic: authentication, database queries, and statistics calculation. The data is stored in a PostgreSQL database hosted on Neon. The system has four main modules: Authentication for secure access, Dashboard for overview, Skills for managing technical skills, and Applications for tracking job applications. A unique aspect is our dual authentication system — HTML routes use session-based auth with cookies, while API routes use JWT Bearer tokens. This allows both web and future mobile app usage."

### Suggested Screenshot/Diagram
- High-level architecture diagram showing: User → Browser → FastAPI Backend → PostgreSQL
- OR a module interaction diagram

### Viva Questions & Answers
**Q1: What is the difference between your HTML routes and API routes?**
A: HTML routes use session-based authentication with cookies and return rendered Jinja2 templates. API routes use JWT Bearer token authentication and return JSON responses. This separation allows both web and programmatic access.

**Q2: Why do you need both session and JWT authentication?**
A: Session auth is simpler for browser-based HTML pages. JWT auth is stateless and better for REST APIs, mobile apps, or third-party integrations. Having both makes the system more flexible.

**Q3: What happens if the database is down?**
A: The application will throw a RuntimeError when trying to get a connection. We have try-except blocks around database operations that catch exceptions and show user-friendly error messages via the error.html template.

---

## Slide 4: System Architecture & Workflow

### Slide Title
System Architecture & Workflow

### PPT Content
**Architecture Pattern:**
- **Model-View-Template (MVT)** — Similar to MVC but adapted for FastAPI
  - Model: `models.py` (database schema definition)
  - View: `app.py` route handlers (business logic)
  - Template: `templates/` (Jinja2 HTML files)

**Request Flow (HTML Route):**
```
1. User Request → FastAPI Router
2. Route Handler → Check Session (login_required_html)
3. Database Query → psycopg (PostgreSQL)
4. Data Processing → Python logic (statistics, search)
5. Template Rendering → Jinja2 + context data
6. HTML Response → Browser
```

**Request Flow (API Route):**
```
1. API Request → FastAPI Router
2. JWT Verification → decode_jwt_token()
3. Database Query → psycopg (PostgreSQL)
4. JSON Response → Return data
```

**Directory Structure:**
```
training_project/
├── app.py              # Main FastAPI app & routes
├── auth.py             # JWT & session auth helpers
├── database.py         # DB connection & initialization
├── models.py           # Schema documentation
├── schemas.py          # Pydantic validation models
├── templates/          # Jinja2 HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   ├── register.html
│   ├── add_skill.html
│   └── add_application.html
├── static/
│   └── style.css       # Custom styling
├── requirements.txt    # Python dependencies
└── render.yaml         # Deployment config
```

### Speaker Notes (30-60 seconds)
"Our system follows the Model-View-Template architecture. The models define the database structure, the views are the FastAPI route handlers in app.py that contain all business logic, and the templates are the Jinja2 HTML files. When a user requests a page, FastAPI routes the request to the appropriate handler. For HTML pages, the handler checks the session, queries the database using psycopg, processes the data — like calculating statistics for the dashboard — and renders a Jinja2 template with the data. For API calls, it verifies the JWT token, queries the database, and returns JSON. The entire backend is in a single app.py file with clear sections for HTML routes, API routes, and error handlers."

### Suggested Screenshot/Diagram
- MVT Architecture diagram with arrows showing data flow
- Directory structure tree diagram

### Viva Questions & Answers
**Q1: Why did you choose MVT over MVC?**
A: FastAPI with Jinja2 naturally fits the MVT pattern. The "View" in MVT is the route handler that processes requests, which is conceptually similar to MVC's Controller but adapted for Python web frameworks.

**Q2: How does the request flow from user to database and back?**
A: User sends HTTP request → FastAPI matches route → Handler checks auth → Handler queries PostgreSQL via psycopg → Data is processed → Template is rendered with context → HTML response sent to browser.

**Q3: What is the role of Jinja2 in your project?**
A: Jinja2 is the templating engine. It allows us to embed Python-like expressions in HTML, use template inheritance with base.html, and dynamically render data from the backend into HTML pages.

---

## Slide 5: Technology Stack

### Slide Title
Technology Stack

### PPT Content
**Backend Framework:**
- **FastAPI 0.104.1** — Modern, fast Python web framework with async support
- **Uvicorn 0.24.0** — ASGI server for running FastAPI
- **Python 3.x** — Core programming language

**Frontend:**
- **Jinja2 3.1.2** — Templating engine for server-side HTML rendering
- **HTML5 / CSS3** — Markup and styling
- **JavaScript** — Client-side interactivity (confirm dialogs)

**Database:**
- **PostgreSQL** — Primary database (hosted on Neon)
- **psycopg[binary]** — PostgreSQL adapter for Python
- **SQLite** — Local development database (migrated to PostgreSQL)

**Authentication & Security:**
- **PyJWT 2.8.0** — JWT token generation and verification
- **python-jose 3.3.0** — JWT encoding/decoding
- **itsdangerous** — Session middleware for cookie-based sessions
- **SessionMiddleware** — Starlette session management

**Validation & Utilities:**
- **Pydantic** — Data validation for API requests/responses (via FastAPI)
- **python-dotenv 1.0.0** — Environment variable management
- **python-multipart 0.0.6** — Form data parsing

**Deployment:**
- **Render** — Cloud platform for hosting
- **Neon PostgreSQL** — Serverless PostgreSQL database

### Speaker Notes (30-60 seconds)
"Our technology stack is built around modern Python web development. FastAPI is our backend framework — it's one of the fastest Python frameworks, supports async operations, and automatically generates Swagger documentation. We use Uvicorn as the ASGI server. For the frontend, we use Jinja2 templates with HTML and CSS — no heavy JavaScript frameworks needed for this project. The database is PostgreSQL, specifically hosted on Neon, a serverless PostgreSQL provider. We use psycopg as the database driver. For authentication, we have a dual system: session-based auth using itsdangerous for HTML pages, and JWT tokens using PyJWT for API routes. All configuration is managed through environment variables using python-dotenv. The entire application is deployed on Render, which handles the hosting and SSL."

### Suggested Screenshot/Diagram
- Technology stack layered diagram:
  - Frontend: HTML/CSS/Jinja2
  - Backend: FastAPI + Uvicorn
  - Database: PostgreSQL (Neon)
  - Deployment: Render

### Viva Questions & Answers
**Q1: Why PostgreSQL and not MySQL or MongoDB?**
A: PostgreSQL is a robust relational database with strong ACID compliance. Our data has clear relationships (students → skills, students → applications), making a relational database the right choice. Neon provides a serverless PostgreSQL that's easy to deploy.

**Q2: What is the advantage of using FastAPI over Flask for this project?**
A: FastAPI provides automatic API documentation, built-in data validation with Pydantic, async support for better concurrency, and type hints that catch errors at development time. It's also generally faster in production.

**Q3: Why did you choose Jinja2 instead of a frontend framework like React?**
A: For this project, Jinja2 is sufficient. It allows server-side rendering, simpler deployment (no separate frontend build step), and is easier to explain in a viva. A React frontend would add unnecessary complexity for a CRUD-based student tracker.

---

## Slide 6: Database Design

### Slide Title
Database Design

### PPT Content
**Database:** PostgreSQL (Neon)
**Schema:** `placement_tracker`

**Table 1: students**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing student ID |
| name | TEXT | NOT NULL | Student full name |
| email | TEXT | UNIQUE, NOT NULL | Login email address |
| password | TEXT | NOT NULL | Hashed password (plain text in current version) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation time |

**Table 2: skills**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing skill ID |
| student_id | INTEGER | FK → students(id), ON DELETE CASCADE | Owner of the skill |
| skill_name | TEXT | NOT NULL | Name of skill (e.g., Python, Java) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When skill was added |

**Table 3: applications**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing application ID |
| student_id | INTEGER | FK → students(id), ON DELETE CASCADE | Owner of the application |
| company_name | TEXT | NOT NULL | Company applied to |
| status | TEXT | DEFAULT 'Applied' | Current status |
| date_applied | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When application was submitted |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

**Relationships:**
- `students` (1) → (N) `skills` — One student can have many skills
- `students` (1) → (N) `applications` — One student can have many applications
- Cascade delete: If a student is deleted, their skills and applications are also deleted

**Data Flow:**
```
User Registration → INSERT INTO students
Add Skill → INSERT INTO skills (student_id from session)
Add Application → INSERT INTO applications (student_id from session)
Dashboard → SELECT with JOINs (implicit via student_id)
```

### Speaker Notes (30-60 seconds)
"Our database has three main tables in the placement_tracker schema. The students table stores user credentials and profile info. The skills table stores each student's skills, linked by student_id. The applications table tracks job applications with company name and status. The key relationship is one-to-many: one student can have many skills and many applications. We use foreign keys with ON DELETE CASCADE, so if a student account is removed, all their associated data is automatically cleaned up. The status field in applications defaults to 'Applied' and can be updated to 'Interview Scheduled', 'Selected', or 'Rejected'. All timestamps are automatically set by PostgreSQL using CURRENT_TIMESTAMP."

### Suggested Screenshot/Diagram
- ER Diagram showing three tables with relationships
- Screenshot of Neon database dashboard showing the tables

### Viva Questions & Answers
**Q1: Why did you use SERIAL PRIMARY KEY instead of UUID?**
A: SERIAL is simpler, auto-incrementing, and more readable for a student tracker. UUIDs are better for distributed systems but add unnecessary complexity here.

**Q2: What is ON DELETE CASCADE and why did you use it?**
A: ON DELETE CASCADE means if a parent record (student) is deleted, all child records (skills, applications) are automatically deleted too. This prevents orphaned records in the database.

**Q3: Why is email marked as UNIQUE?**
A: To prevent duplicate registrations. Each student must have a unique email address, which also serves as the login username.

---

## Slide 7: User Authentication & Session Management

### Slide Title
User Authentication & Session Management

### PPT Content
**Authentication Mechanisms:**

**1. Session-Based Authentication (HTML Routes)**
- Uses Starlette's `SessionMiddleware` with `itsdangerous`
- Session data stored in encrypted cookies
- Session secret key from environment variable `FLASK_SECRET_KEY`
- Session max age: 24 hours (86400 seconds)
- Routes protected by `login_required_html()` dependency

**2. JWT-Based Authentication (API Routes)**
- Uses `PyJWT` library with HS256 algorithm
- Token payload: `{ user_id, exp }`
- Token expiry: 24 hours (configurable via `JWT_EXP_DELTA_HOURS`)
- Secret key from environment variable `JWT_SECRET_KEY`
- Routes protected by `login_required_api()` dependency

**Key Routes:**
- `GET /register` — Display registration form
- `POST /register` — Create new student account
- `GET /login` — Display login form
- `POST /login` — Authenticate and create session
- `GET /logout` — Clear session and redirect to login
- `POST /api/login` — Return JWT token for API access

**Security Features:**
- Password validation (minimum 6 characters)
- Email uniqueness check
- Session-based access control for HTML pages
- Bearer token authentication for API endpoints
- Protected routes redirect unauthenticated users

**Current Limitation:**
- Passwords stored as plain text (not hashed) — should use bcrypt/werkzeug in production

### Speaker Notes (30-60 seconds)
"Our system implements dual authentication. For HTML pages, we use session-based authentication. When a user logs in via POST /login, their user_id and name are stored in an encrypted session cookie using Starlette's SessionMiddleware. The session lasts 24 hours. For API routes, we use JWT tokens. When a user calls POST /api/login with valid credentials, they receive a JWT token containing their user_id and expiry time. This token must be included in the Authorization header as a Bearer token for subsequent API calls. Both systems protect their respective routes — HTML routes check the session, API routes verify the JWT. A note for production: currently passwords are stored in plain text, which is not secure. In a real deployment, we would use bcrypt hashing."

### Suggested Screenshot/Diagram
- Authentication flow diagram showing both session and JWT flows
- Screenshot of login page and registration page

### Viva Questions & Answers
**Q1: What is the difference between session-based and JWT authentication?**
A: Session auth stores user state on the server (in memory or database) and uses a session ID in cookies. JWT is stateless — the token contains all user info and is verified on each request without server-side storage.

**Q2: Why do you store passwords in plain text? Is that secure?**
A: No, it's not secure. This is a limitation of the current implementation for demonstration purposes. In production, passwords should be hashed using bcrypt or Argon2 before storing. The project would need to implement password hashing for real-world use.

**Q3: What happens when a session expires?**
A: After 24 hours, the session cookie becomes invalid. The user is redirected to the login page when they try to access a protected route. Similarly, JWT tokens expire after 24 hours and return a 401 Unauthorized error.

---

## Slide 8: Core Features

### Slide Title
Core Features

### PPT Content
**Feature 1: User Registration**
- Route: `GET /register`, `POST /register`
- Fields: Name, Email, Password, Confirm Password
- Validation: All fields required, password min 6 chars, passwords must match, email uniqueness check
- Template: `templates/register.html`
- On success: Redirect to login page

**Feature 2: User Login**
- Route: `GET /login`, `POST /login`
- Fields: Email, Password
- Validation: Both fields required
- On success: Session created with user_id and user_name, redirect to dashboard
- On failure: Error message displayed on login page

**Feature 3: Dashboard**
- Route: `GET /dashboard`
- Displays: Welcome message, student profile, statistics cards, skills list, applications table
- Statistics calculated dynamically:
  - Total Skills: `len(skills)`
  - Total Applications: `len(applications)`
  - Interviews: Count where status starts with "interview"
  - Selected: Count where status is "selected"
- Search functionality: Filter applications by company name (query parameter `?search=`)
- Template: `templates/dashboard.html`

**Feature 4: Skills Management**
- Add Skill: `GET /add_skill`, `POST /add_skill`
  - Field: Skill name (e.g., Python, Java, React)
  - Template: `templates/add_skill.html`
- Delete Skill: `POST /delete_skill/{skill_id}`
  - Verifies skill ownership before deletion
  - Returns JSON response for AJAX or redirects

**Feature 5: Applications Management**
- Add Application: `GET /add_application`, `POST /add_application`
  - Fields: Company name, Status (default: "Applied")
  - Status options: Applied, Interview Scheduled, Selected, Rejected
  - Template: `templates/add_application.html`
- Search Applications: `GET /dashboard?search=company_name`
  - SQL LIKE query for partial matching
  - Shows result count when search is active

**Feature 6: REST API**
- `POST /api/register` — JSON registration
- `POST /api/login` — Returns JWT token
- `GET /api/skills` — Get all skills (JWT required)
- `POST /api/skills` — Add skill (JWT required)
- `DELETE /api/skills/{skill_id}` — Delete skill (JWT required)
- `GET /api/applications` — Get applications with optional search (JWT required)
- `POST /api/applications` — Add application (JWT required)
- `GET /api/student/{student_id}` — Get student info (JWT required)

### Speaker Notes (30-60 seconds)
"Our system has six core features. First, user registration with full validation — name, email, two password fields with matching check. Second, login with session creation. Third, the dashboard is the heart of the system — it shows a welcome message, profile info, four statistics cards that are calculated dynamically from the database, a list of all skills with delete buttons, and a table of all applications with status badges. The dashboard also has a search bar to filter applications by company name. Fourth, skills management — add and delete skills. Fifth, applications management — add applications with status tracking. Sixth, a complete REST API with JWT authentication for future mobile app integration. All features are protected — unauthenticated users are redirected to login."

### Suggested Screenshot/Diagram
- Screenshot of Dashboard showing all features (statistics, skills, applications)
- Feature breakdown diagram

### Viva Questions & Answers
**Q1: How are the dashboard statistics calculated?**
A: In the dashboard route handler, we query all skills and applications for the user, then use Python to count: total_skills is the length of the skills list, total_applications is the length of applications, interviews count checks if status starts with 'interview', and selected count checks for exact 'selected' status.

**Q2: Can a user delete another user's skill?**
A: No. In the delete_skill route, we first verify that the skill belongs to the current logged-in user by checking `SELECT id FROM skills WHERE id = %s AND student_id = %s`. If not found, we return a 404 error.

**Q3: What status values can an application have?**
A: The default is 'Applied'. Other possible values shown in the code are 'Interview Scheduled', 'Selected', and 'Rejected'. The status field is a free-text field, so users can enter any value, but these are the intended options.

---

## Slide 9: Deployment & Database Integration

### Slide Title
Deployment & Database Integration

### PPT Content
**Deployment Platform: Render**
- Service type: Web service
- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Auto-deploy from Git repository
- Free tier available for testing

**Database: Neon PostgreSQL**
- Serverless PostgreSQL provider
- Connection via `DATABASE_URL` environment variable
- Schema: `placement_tracker` (configurable via `PG_SCHEMA`)
- Connection pooling handled by psycopg

**Configuration Files:**
- `render.yaml` — Render deployment configuration
- `requirements.txt` — Python dependencies
- `.env` — Environment variables (not in Git)
  - `DATABASE_URL` — Neon PostgreSQL connection string
  - `FLASK_SECRET_KEY` — Session encryption key
  - `JWT_SECRET_KEY` — JWT signing key
  - `PG_SCHEMA` — Database schema name

**Database Initialization:**
- `init_db()` in `database.py` creates schema and tables on first run
- `migrate_sqlite_to_postgres()` migrates local SQLite data to PostgreSQL if present
- Tables created with `CREATE TABLE IF NOT EXISTS` for idempotency

**Environment Variables Used:**
| Variable | Purpose | Default |
|----------|---------|---------|
| DATABASE_URL | PostgreSQL connection string | Required |
| FLASK_SECRET_KEY | Session cookie encryption | 'your_secret_key...' |
| JWT_SECRET_KEY | JWT token signing | 'your_jwt_secret...' |
| JWT_EXP_DELTA_HOURS | Token expiry time | 24 |
| PG_SCHEMA | Database schema name | 'placement_tracker' |

**Local Development:**
- Run with: `python main.py` or `uvicorn main:app --reload`
- SQLite used locally if DATABASE_URL is not set
- Auto-migration from SQLite to PostgreSQL on first PostgreSQL connection

### Speaker Notes (30-60 seconds)
"For deployment, we use Render, a cloud platform that supports Python web services. The render.yaml file specifies the build and start commands. The database is hosted on Neon, a serverless PostgreSQL provider. The connection is configured via the DATABASE_URL environment variable, which Render injects automatically. On the first run, the init_db function creates the placement_tracker schema and all three tables if they don't exist. We also have a migration function that can move data from a local SQLite database to PostgreSQL. For local development, if DATABASE_URL is not set, the app can fall back to SQLite. All sensitive configuration like database credentials and secret keys are stored as environment variables, never in the code repository."

### Suggested Screenshot/Diagram
- Screenshot of Render dashboard showing the deployed service
- Screenshot of Neon database dashboard
- render.yaml file content

### Viva Questions & Answers
**Q1: How does the app know whether to use SQLite or PostgreSQL?**
A: The app checks if the DATABASE_URL environment variable is set. If it is, it uses PostgreSQL via psycopg. If not, it falls back to SQLite for local development.

**Q2: What is the purpose of render.yaml?**
A: render.yaml is a Render-specific configuration file that tells the platform how to build and run the application — what dependencies to install and what command to start the server with.

**Q3: How do you handle database schema changes in production?**
A: Currently, the app uses CREATE TABLE IF NOT EXISTS, which is good for initial setup but not for schema migrations. For production, we would use a migration tool like Alembic to manage schema changes safely.

---

## Slide 10: Testing, Results, Future Scope & Conclusion

### Slide Title
Testing, Results, Future Scope & Conclusion

### PPT Content
**Testing Performed:**
- **Functional Testing:**
  - User registration with valid/invalid data
  - Login with correct/incorrect credentials
  - Dashboard statistics accuracy
  - Skill add/delete operations
  - Application add/search operations
- **Authentication Testing:**
  - Session creation and expiry
  - JWT token generation and validation
  - Protected route access control
- **Database Testing:**
  - Table creation and relationships
  - Foreign key constraints (ON DELETE CASCADE)
  - Data migration from SQLite to PostgreSQL

**Results Achieved:**
- Fully functional web application deployed on Render
- All core features working: Registration, Login, Dashboard, Skills, Applications
- Dual authentication system operational (Session + JWT)
- PostgreSQL database with proper schema and relationships
- Responsive UI with custom CSS styling
- REST API with 7 endpoints fully functional
- Search functionality working with SQL LIKE queries

**Limitations of Current System:**
- Passwords stored in plain text (not hashed)
- No email verification during registration
- No password reset functionality
- No admin panel or role-based access
- No resume upload or parsing
- No company job feed integration
- No email/SMS notifications

**Future Scope:**
1. **Security Enhancements:**
   - Implement bcrypt password hashing
   - Add email verification with OTP
   - Implement password reset via email
   - Add rate limiting for login attempts

2. **Feature Enhancements:**
   - Admin panel for placement officers
   - Resume upload and parsing
   - Company-wise job posting feed
   - Application status history/audit log
   - Bulk import skills/applications
   - Export data to PDF/Excel

3. **Technical Improvements:**
   - Migrate to SQLAlchemy ORM
   - Add Alembic for database migrations
   - Implement Redis caching for statistics
   - Add Docker containerization
   - Implement CI/CD pipeline

4. **Mobile & Integration:**
   - React Native mobile app using the REST API
   - Integration with LinkedIn/Indeed job APIs
   - Calendar sync for interview schedules

**Conclusion:**
The Student Placement Tracker successfully addresses the problem of disorganized placement tracking. Built with FastAPI and PostgreSQL, it provides a robust, scalable platform for students to manage their placement journey. The dual authentication system, REST API, and clean architecture make it suitable for both current web use and future expansion. The project demonstrates effective use of modern Python web technologies and cloud deployment.

### Speaker Notes (30-60 seconds)
"We tested the application thoroughly — registration, login, dashboard statistics, skill management, application tracking, and search all work correctly. The dual authentication system was tested with both session cookies and JWT tokens. The database relationships work as expected, with cascade delete functioning properly. The application is successfully deployed on Render with Neon PostgreSQL. However, we acknowledge limitations: passwords are not hashed, there's no email verification, and no admin features. For future work, we plan to add password hashing with bcrypt, email OTP verification, an admin panel, resume uploads, and a mobile app using our existing REST API. In conclusion, this project demonstrates a complete full-stack web application using modern Python technologies, with a clean architecture that's ready for production enhancements."

### Suggested Screenshot/Diagram
- Screenshot of deployed application on Render
- Testing checklist or test results table
- Future scope roadmap diagram

### Viva Questions & Answers
**Q1: What is the biggest challenge you faced during development?**
A: Migrating from Flask to FastAPI required rethinking the authentication system. FastAPI doesn't have built-in session management like Flask, so we had to implement it using Starlette's SessionMiddleware and itsdangerous. Also, adapting Jinja2 templates to work with FastAPI's async request handling required careful configuration.

**Q2: How would you improve the security of this application?**
A: First, implement bcrypt password hashing. Second, add email verification with OTP during registration. Third, implement rate limiting on login to prevent brute force attacks. Fourth, use HTTPS in production (Render provides this automatically). Fifth, add CSRF protection for form submissions.

**Q3: What did you learn from this project?**
A: I learned how to build a production-ready FastAPI application with both server-rendered HTML and REST API endpoints. I gained experience with PostgreSQL, JWT authentication, session management, and cloud deployment on Render. The migration from Flask to FastAPI taught me the differences between synchronous and asynchronous web frameworks.

---

# End of Presentation

**Total Slides:** 10 (excluding Title and Thank You slides)
**Recommended Presentation Time:** 10-15 minutes + Q&A
**Viva Preparation:** Review all FastAPI routes, database schema, and authentication flow