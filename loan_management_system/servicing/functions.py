import sqlite3
import datetime
from loan_management_system.database.db_setup import get_db_connection
from loan_management_system.origination.models import LoanApplication # For type hinting if passing LoanApplication objects
from .models import Loan # For type hinting or constructing Loan objects if needed

# Global active_loans list is removed

def activate_loan(application_id: int, principal_amount: float, interest_rate: float, term: int, initial_status: str = "Active") -> int:
    """
    Creates a new loan record in the database and returns its ID.
    The loan is linked to a loan application via application_id.
    """
    conn = None
    new_loan_id = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        activation_date = datetime.datetime.now().isoformat()

        sql = """
        INSERT INTO loans (application_id, principal, interest_rate, term, status, activation_date)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (application_id, principal_amount, interest_rate, term, initial_status, activation_date))
        conn.commit()
        new_loan_id = cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error in activate_loan: {e}")
        # Optionally re-raise or handle
    finally:
        if conn:
            conn.close()
    return new_loan_id

def get_loan_by_id(loan_id: int) -> dict:
    """
    Retrieves a loan by its ID from the database.
    Returns a dictionary representing the loan or None if not found.
    """
    conn = None
    loan_data = None
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row # Access columns by name
        cursor = conn.cursor()

        sql = "SELECT * FROM loans WHERE id = ?"
        cursor.execute(sql, (loan_id,))
        row = cursor.fetchone()

        if row:
            loan_data = dict(row) # Convert sqlite3.Row to a dictionary

    except sqlite3.Error as e:
        print(f"Database error in get_loan_by_id: {e}")
    finally:
        if conn:
            conn.close()
    return loan_data

def record_payment(loan_id: int, payment_amount: float) -> int | None:
    """
    Records a payment against a loan in the database.

    Args:
        loan_id (int): The ID of the loan for which the payment is made.
        payment_amount (float): The amount of the payment.

    Returns:
        int | None: The ID of the newly recorded payment, or None if an error occurred
                    (e.g., invalid amount, loan_id not found - though FK constraint handles this at DB level).
    """
    if payment_amount <= 0:
        print("Payment amount must be positive.")
        return None

    # Check if loan exists (optional, as FK constraint will catch it, but better for UX)
    # For this exercise, we'll rely on FK constraint or assume valid loan_id for brevity.
    # existing_loan = get_loan_by_id(loan_id)
    # if not existing_loan:
    #     print(f"Loan with ID {loan_id} not found. Cannot record payment.")
    #     return None

    conn = None
    payment_id = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        payment_date = datetime.datetime.now().isoformat()

        sql = """
        INSERT INTO payments (loan_id, payment_date, amount_paid)
        VALUES (?, ?, ?)
        """
        cursor.execute(sql, (loan_id, payment_date, payment_amount))
        conn.commit()
        payment_id = cursor.lastrowid
        print(f"Payment of {payment_amount} recorded for loan ID {loan_id}. Payment ID: {payment_id}")

    except sqlite3.Error as e:
        # sqlite3.IntegrityError will be raised if loan_id does not exist in loans table (due to FOREIGN KEY constraint)
        print(f"Database error in record_payment: {e}")
        # Rollback might be needed if conn was kept open for multiple operations, but here it's fine.
    finally:
        if conn:
            conn.close()
    return payment_id

def get_payments_for_loan(loan_id: int) -> list[dict]:
    """
    Retrieves all payments made for a specific loan, ordered by payment date.

    Args:
        loan_id (int): The ID of the loan.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents a payment.
                    Returns an empty list if no payments are found or loan_id is invalid.
    """
    conn = None
    payments_list = []
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row # Access columns by name
        cursor = conn.cursor()

        sql = "SELECT * FROM payments WHERE loan_id = ? ORDER BY payment_date"
        cursor.execute(sql, (loan_id,))
        rows = cursor.fetchall()

        for row in rows:
            payments_list.append(dict(row))

    except sqlite3.Error as e:
        print(f"Database error in get_payments_for_loan: {e}")
    finally:
        if conn:
            conn.close()
    return payments_list

def get_loan_balance(loan_id: int) -> float | None:
    """
    Calculates the remaining balance for a loan.

    Args:
        loan_id (int): The ID of the loan.

    Returns:
        float | None: The calculated remaining balance (principal - total payments).
                      Returns None if the loan is not found or principal is missing.
    """
    loan_details = get_loan_by_id(loan_id)

    if not loan_details:
        print(f"Loan with ID {loan_id} not found for balance calculation.")
        return None

    principal = loan_details.get('principal')
    if principal is None:
        print(f"Principal amount not found for loan ID {loan_id}.")
        return None # Should not happen if DB schema is enforced

    payments = get_payments_for_loan(loan_id)
    total_payments_made = sum(payment.get('amount_paid', 0) for payment in payments)

    balance = principal - total_payments_made
    return balance

def list_all_loans(status_filter: str = None) -> list[dict]:
    """
    Retrieves all loans, optionally filtered by status.

    Args:
        status_filter (str, optional): If provided, only loans with this status
                                       will be returned. Defaults to None (all loans).

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents a loan.
                    Returns an empty list if no loans are found.
    """
    conn = None
    loans_list = []
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row # Access columns by name
        cursor = conn.cursor()

        sql = "SELECT * FROM loans"
        params = [] # Use a list for params

        if status_filter and status_filter.strip(): # Check if filter is provided and not just whitespace
            sql += " WHERE status = ?"
            params.append(status_filter)

        sql += " ORDER BY id" # Order by ID for consistency

        cursor.execute(sql, tuple(params)) # Execute expects a tuple for parameters
        rows = cursor.fetchall()

        for row in rows:
            loans_list.append(dict(row))

    except sqlite3.Error as e:
        print(f"Database error in list_all_loans: {e}")
    finally:
        if conn:
            conn.close()
    return loans_list
