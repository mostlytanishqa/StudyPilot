
import sqlite3
from datetime import date, timedelta

from config import DB_PATH


def get_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    """Create all database tables and insert initial data."""

    with get_connection() as conn:

        conn.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            daily_hours REAL DEFAULT 3,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            exam_date TEXT
        );

        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            difficulty TEXT DEFAULT 'Medium',
            completed INTEGER DEFAULT 0,
            FOREIGN KEY(subject_id)
                REFERENCES subjects(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            study_date TEXT NOT NULL,
            hours REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY(topic_id)
                REFERENCES topics(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            study_date TEXT NOT NULL,
            hours REAL NOT NULL,
            FOREIGN KEY(subject_id)
                REFERENCES subjects(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            accuracy REAL NOT NULL,
            attempted_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS quiz_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attempt_id INTEGER NOT NULL,
            question_id TEXT NOT NULL,
            selected_answer TEXT,
            correct_answer TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            FOREIGN KEY(attempt_id)
                REFERENCES quiz_attempts(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS revisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            review_date TEXT NOT NULL,
            interval_days INTEGER DEFAULT 1,
            ease_factor REAL DEFAULT 2.5,
            repetitions INTEGER DEFAULT 0
        );
        """)

        student_count = conn.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

        if student_count == 0:
            conn.execute(
                "INSERT INTO students (name, daily_hours) VALUES (?, ?)",
                ("Student", 3)
            )

        subject_count = conn.execute(
            "SELECT COUNT(*) FROM subjects"
        ).fetchone()[0]

        if subject_count == 0:
            seed_sample_data(conn)


def seed_sample_data(conn):
    """Insert sample subjects and topics for first-time users."""

    sample_data = {
        "Quantitative Aptitude": [
            ("Percentage", "Medium"),
            ("Profit and Loss", "Medium"),
            ("Time and Work", "Hard"),
            ("Simple Interest", "Easy"),
            ("Number System", "Hard")
        ],

        "Logical Reasoning": [
            ("Number Series", "Easy"),
            ("Coding and Decoding", "Medium"),
            ("Blood Relations", "Medium"),
            ("Direction Sense", "Easy"),
            ("Seating Arrangement", "Hard")
        ],

        "Data Interpretation": [
            ("Bar Graphs", "Easy"),
            ("Pie Charts", "Medium"),
            ("Tables", "Medium"),
            ("Line Graphs", "Hard")
        ],

        "Computer Fundamentals": [
            ("Operating Systems", "Medium"),
            ("Computer Networks", "Hard"),
            ("Database Management", "Medium"),
            ("Python Basics", "Easy"),
            ("Data Structures", "Hard")
        ]
    }

    for subject, topics in sample_data.items():

        exam_date = (
            date.today() + timedelta(days=30)
        ).isoformat()

        cursor = conn.execute(
            "INSERT INTO subjects (name, exam_date) VALUES (?, ?)",
            (subject, exam_date)
        )

        subject_id = cursor.lastrowid

        for topic, difficulty in topics:
            conn.execute("""
                INSERT INTO topics
                (subject_id, name, difficulty)
                VALUES (?, ?, ?)
            """, (subject_id, topic, difficulty))


def get_student():
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM students ORDER BY id LIMIT 1"
        ).fetchone()

        return dict(row) if row else None


def update_student(name, daily_hours):
    if not name.strip():
        raise ValueError("Student name cannot be empty.")

    if not 0.5 <= daily_hours <= 16:
        raise ValueError("Daily hours must be between 0.5 and 16.")

    with get_connection() as conn:
        conn.execute("""
            UPDATE students
            SET name = ?, daily_hours = ?
            WHERE id = (SELECT MIN(id) FROM students)
        """, (name.strip(), daily_hours))


def get_subjects():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM subjects ORDER BY name"
        ).fetchall()

        return [dict(row) for row in rows]


def add_subject(name, exam_date):
    name = name.strip()

    if not name:
        raise ValueError("Subject name is required.")

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO subjects (name, exam_date)
            VALUES (?, ?)
        """, (name, exam_date))


def add_topic(subject_id, name, difficulty):
    name = name.strip()

    if not name:
        raise ValueError("Topic name is required.")

    if difficulty not in ("Easy", "Medium", "Hard"):
        raise ValueError("Invalid difficulty.")

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO topics
            (subject_id, name, difficulty)
            VALUES (?, ?, ?)
        """, (subject_id, name, difficulty))


def get_topics():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                topics.*,
                subjects.name AS subject_name,
                subjects.exam_date
            FROM topics
            JOIN subjects
                ON topics.subject_id = subjects.id
            ORDER BY subjects.name, topics.name
        """).fetchall()

        return [dict(row) for row in rows]


def update_topic_status(topic_id, completed):
    with get_connection() as conn:
        conn.execute("""
            UPDATE topics
            SET completed = ?
            WHERE id = ?
        """, (int(bool(completed)), topic_id))


def get_dashboard_stats():
    with get_connection() as conn:

        total = conn.execute(
            "SELECT COUNT(*) FROM topics"
        ).fetchone()[0]

        completed = conn.execute(
            "SELECT COUNT(*) FROM topics WHERE completed = 1"
        ).fetchone()[0]

        subjects = conn.execute(
            "SELECT COUNT(*) FROM subjects"
        ).fetchone()[0]

        quizzes = conn.execute(
            "SELECT COUNT(*) FROM quiz_attempts"
        ).fetchone()[0]

        study_hours = conn.execute(
            "SELECT COALESCE(SUM(hours), 0) FROM study_sessions"
        ).fetchone()[0]

        return {
            "subjects": subjects,
            "total_topics": total,
            "completed": completed,
            "pending": total - completed,
            "percentage": round(completed / total * 100)
                if total else 0,
            "quizzes": quizzes,
            "study_hours": round(study_hours, 2)
        }


def save_study_session(subject_id, hours):
    if hours <= 0:
        raise ValueError("Study hours must be positive.")

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO study_sessions
            (subject_id, study_date, hours)
            VALUES (?, ?, ?)
        """, (subject_id, date.today().isoformat(), hours))


def get_weekly_activity():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT study_date, SUM(hours) AS hours
            FROM study_sessions
            WHERE study_date >= date('now', '-6 days')
            GROUP BY study_date
            ORDER BY study_date
        """).fetchall()

        return [dict(row) for row in rows]


def get_upcoming_exams():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT name, exam_date
            FROM subjects
            WHERE exam_date >= ?
            ORDER BY exam_date
        """, (date.today().isoformat(),)).fetchall()

        return [dict(row) for row in rows]


def save_schedule(schedule):
    with get_connection() as conn:

        conn.execute("DELETE FROM schedules")

        for item in schedule:
            conn.execute("""
                INSERT INTO schedules
                (topic_id, study_date, hours)
                VALUES (?, ?, ?)
            """, (
                item["topic_id"],
                item["date"],
                item["hours"]
            ))


def get_schedule():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                schedules.*,
                topics.name AS topic_name,
                subjects.name AS subject_name
            FROM schedules
            JOIN topics
                ON schedules.topic_id = topics.id
            JOIN subjects
                ON topics.subject_id = subjects.id
            ORDER BY schedules.study_date
        """).fetchall()

        return [dict(row) for row in rows]
