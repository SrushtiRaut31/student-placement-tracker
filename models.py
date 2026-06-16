# Student Placement Tracker - Database Models
# SQLAlchemy-style model definitions (for documentation/reference)
# Actual database operations are handled via raw SQL with psycopg2

# These classes represent the database schema for documentation purposes.
# The actual tables are created in database.py using raw SQL.
# RealDictCursor from psycopg2.extras returns rows as dictionary-like objects.

"""
Database Schema:

Table: students
  - id: SERIAL PRIMARY KEY
  - name: TEXT NOT NULL
  - email: TEXT UNIQUE NOT NULL
  - password: TEXT NOT NULL
  - created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

Table: skills
  - id: SERIAL PRIMARY KEY
  - student_id: INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE
  - skill_name: TEXT NOT NULL
  - created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

Table: applications
  - id: SERIAL PRIMARY KEY
  - student_id: INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE
  - company_name: TEXT NOT NULL
  - status: TEXT DEFAULT 'Applied'
  - date_applied: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  - created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
"""