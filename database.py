# Student Placement Tracker - Database Module
# Handles PostgreSQL (Neon) connection and initialization

import os
import sqlite3
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

# Database configuration
SQLITE_DATABASE = 'database.db'
PG_SCHEMA = os.getenv('PG_SCHEMA', 'placement_tracker')


def get_database_url():
    """
    Read DATABASE_URL from environment lazily (at call time, not import time).
    This ensures .env is loaded before this function is called.
    """
    url = os.getenv('DATABASE_URL')
    if not url:
        raise RuntimeError('DATABASE_URL is not configured. Set it in the .env file or environment.')
    return url


def get_db_connection():
    """
    Create and return a PostgreSQL database connection.
    Uses DATABASE_URL from .env or environment variables.
    The search_path is set and the transaction is committed to leave
    the connection in a clean state for the caller.
    """
    database_url = get_database_url()
    conn = psycopg2.connect(database_url)
    with conn.cursor() as cursor:
        cursor.execute(sql.SQL('SET search_path TO {}').format(sql.Identifier(PG_SCHEMA)))
    conn.commit()
    return conn


def get_db_cursor(conn):
    """Return a RealDictCursor for the given connection."""
    return conn.cursor(cursor_factory=RealDictCursor)


def migrate_sqlite_to_postgres():
    """
    Migrate existing SQLite data to PostgreSQL if a local SQLite database exists.
    This preserves students, skills, and applications data.
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
    get_database_url()  # Validate DATABASE_URL is available

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