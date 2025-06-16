import sqlite3
import datetime
from loan_management_system.database.db_setup import get_db_connection
# We'll keep LoanApplication import for type hinting, but functions will primarily return dicts or IDs from DB
from .models import LoanApplication

# Global loan_applications list is removed

def create_loan_application(applicant_name: str, loan_amount: float, purpose: str) -> int:
    """
    Creates a new loan application in the database and returns its ID.
    """
    conn = None
    application_id = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        application_date = datetime.datetime.now().isoformat()

        sql = """
        INSERT INTO loan_applications (applicant_name, loan_amount, purpose, application_date, status)
        VALUES (?, ?, ?, ?, ?)
        """
        # Status defaults to 'Pending' in DB schema, but we can be explicit
        cursor.execute(sql, (applicant_name, loan_amount, purpose, application_date, 'Pending'))
        conn.commit()
        application_id = cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error in create_loan_application: {e}")
        # Optionally re-raise or handle more gracefully
    finally:
        if conn:
            conn.close()
    return application_id


def get_loan_application_by_id(application_id: int) -> dict:
    """
    Retrieves a loan application by its ID from the database.
    Returns a dictionary representing the application or None if not found.
    """
    conn = None
    application_data = None
    try:
        conn = get_db_connection()
        # Make sure row_factory is set to sqlite3.Row to access columns by name easily
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        sql = "SELECT * FROM loan_applications WHERE id = ?"
        cursor.execute(sql, (application_id,))
        row = cursor.fetchone()

        if row:
            # Convert sqlite3.Row to a dictionary
            application_data = dict(row)

    except sqlite3.Error as e:
        print(f"Database error in get_loan_application_by_id: {e}")
    finally:
        if conn:
            conn.close()
    return application_data

def list_all_applications(status_filter: str = None) -> list[dict]:
    """
    Retrieves all loan applications, optionally filtered by status.

    Args:
        status_filter (str, optional): If provided, only applications with this status
                                       will be returned. Defaults to None (all applications).

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents a loan application.
                    Returns an empty list if no applications are found.
    """
    conn = None
    applications_list = []
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row # Access columns by name
        cursor = conn.cursor()

        sql = "SELECT * FROM loan_applications"
        params = [] # Use a list for params

        if status_filter and status_filter.strip(): # Check if filter is provided and not just whitespace
            sql += " WHERE status = ?"
            params.append(status_filter)

        sql += " ORDER BY id" # Optional: order by ID or date

        cursor.execute(sql, tuple(params)) # Execute expects a tuple for parameters
        rows = cursor.fetchall()

        for row in rows:
            applications_list.append(dict(row))

    except sqlite3.Error as e:
        print(f"Database error in list_all_applications: {e}")
    finally:
        if conn:
            conn.close()
    return applications_list
