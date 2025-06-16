import sqlite3
import datetime

DATABASE_NAME = 'loan_system.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("PRAGMA foreign_keys = ON;") # Enforce foreign key constraints
    return conn

def create_tables():
    """Creates the necessary tables in the database if they don't already exist."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Table for Loan Applications
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS loan_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant_name TEXT NOT NULL,
            loan_amount REAL NOT NULL,
            purpose TEXT,
            application_date TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
        """)

        # Table for Loans
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            principal REAL NOT NULL,
            interest_rate REAL NOT NULL,
            term INTEGER NOT NULL,
            status TEXT NOT NULL,
            activation_date TEXT,
            FOREIGN KEY (application_id) REFERENCES loan_applications (id)
        )
        """)

        # Table for Payments
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_id INTEGER NOT NULL,
            payment_date TEXT NOT NULL,
            amount_paid REAL NOT NULL,
            FOREIGN KEY (loan_id) REFERENCES loans (id)
        )
        """)

        conn.commit()
        print("Tables created successfully (if they didn't exist, payments table added/updated).")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    import os

    # Original DATABASE_NAME might be relative (e.g., 'loan_system.db')
    # We want to ensure it's created in the same directory as this script.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path_for_direct_execution = os.path.join(script_dir, DATABASE_NAME)

    # Temporarily modify DATABASE_NAME for the create_tables() call in this direct execution context
    # This is a bit of a workaround for the current structure. A cleaner way would be to pass db_path to functions.
    original_db_name = DATABASE_NAME
    DATABASE_NAME = db_path_for_direct_execution

    print(f"Database will be created at: {os.path.abspath(DATABASE_NAME)}")
    create_tables()

    # Restore original DATABASE_NAME if it matters for other potential code in this block (not currently the case)
    DATABASE_NAME = original_db_name
