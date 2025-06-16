import sqlite3
from loan_management_system.origination.functions import get_loan_application_by_id
# LoanApplication model import is removed as we primarily work with dicts from DB now
# from loan_management_system.origination.models import LoanApplication
from loan_management_system.database.db_setup import get_db_connection

def assess_application(application_id: int, loan_amount_threshold: float = 20000.0) -> bool:
    """
    Assesses a loan application based on its amount and updates its status in the database.

    Args:
        application_id (int): The ID of the loan application to assess.
        loan_amount_threshold (float): The threshold for loan approval.
                                       Loans with amount <= threshold are approved.

    Returns:
        bool: True if the application is approved, False otherwise.
              Returns False if the application is not found.
    """
    application_data = get_loan_application_by_id(application_id)

    if not application_data:
        # Or raise ValueError(f"Application with ID {application_id} not found.")
        print(f"Application with ID {application_id} not found for assessment.")
        return False

    loan_amount = application_data.get('loan_amount')
    if loan_amount is None:
        # Handle cases where loan_amount might be missing, though schema implies NOT NULL
        print(f"Loan amount missing for application ID {application_id}.")
        return False # Or raise error

    decision = "Approved" if loan_amount <= loan_amount_threshold else "Rejected"

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "UPDATE loan_applications SET status = ? WHERE id = ?"
        cursor.execute(sql, (decision, application_id))
        conn.commit()

        print(f"Application ID {application_id} assessed. Decision: {decision}. Status updated in DB.")

    except sqlite3.Error as e:
        print(f"Database error in assess_application while updating status: {e}")
        # Depending on policy, we might want to indicate failure differently.
        # For now, if DB update fails, the function might still return based on logic,
        # but the status in DB is not updated. This could be problematic.
        # Consider re-raising or returning a specific error code/value.
        return False # If DB update fails, consider the assessment incomplete or failed.
    finally:
        if conn:
            conn.close()

    return decision == "Approved"

def get_application_status(application_id: int) -> str | None:
    """
    Retrieves the status of a specific loan application.

    Args:
        application_id (int): The ID of the loan application.

    Returns:
        str | None: The status of the application (e.g., 'Pending', 'Approved', 'Rejected')
                    if found, otherwise None.
    """
    application_data = get_loan_application_by_id(application_id)

    if application_data:
        return application_data.get('status')
    return None
