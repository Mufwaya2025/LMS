import sqlite3
from datetime import datetime, timedelta # Corrected import for datetime object
from loan_management_system.database.db_setup import get_db_connection
from loan_management_system.servicing.functions import get_loan_balance, list_all_loans

def update_loan_status(loan_id: int, new_status: str) -> bool:
    """
    Updates the status of a specific loan in the database.

    Args:
        loan_id (int): The ID of the loan to update.
        new_status (str): The new status to set for the loan.

    Returns:
        bool: True if the loan status was successfully updated (row was affected), False otherwise.
    """
    conn = None
    updated = False
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "UPDATE loans SET status = ? WHERE id = ?"
        cursor.execute(sql, (new_status, loan_id))
        conn.commit()

        if cursor.rowcount > 0:
            updated = True
            print(f"Loan ID {loan_id} status updated to '{new_status}'.")
        else:
            print(f"Loan ID {loan_id} not found or status already '{new_status}'. No update made.")

    except sqlite3.Error as e:
        print(f"Database error in update_loan_status: {e}")
    finally:
        if conn:
            conn.close()
    return updated

def identify_delinquent_loans(days_active_for_minimal_payment_check: int = 30,
                               principal_paid_percentage_threshold: float = 0.10) -> list[dict]:
    """
    Identifies potentially delinquent loans based on simplified criteria.
    Placeholder logic: Checks if an active loan, after a certain period, has paid less than a
    threshold percentage of its principal.

    Args:
        days_active_for_minimal_payment_check (int): Number of days a loan must be active
                                                     before this check applies.
        principal_paid_percentage_threshold (float): The minimum percentage of principal that
                                                     should have been paid after the check period.

    Returns:
        list[dict]: A list of loan dictionaries identified as potentially delinquent.
    """
    active_loans = list_all_loans(status_filter='Active')
    delinquent_loans = []

    print(f"Identifying delinquent loans. Checking {len(active_loans)} active loans...")

    for loan in active_loans:
        loan_id = loan.get('id')
        principal = loan.get('principal')
        activation_date_str = loan.get('activation_date')

        if not all([loan_id, principal is not None, activation_date_str]):
            print(f"Skipping loan due to missing data: ID {loan_id}, Principal {principal}, Activation Date {activation_date_str}")
            continue

        try:
            activation_date = datetime.fromisoformat(activation_date_str)
        except ValueError:
            print(f"Could not parse activation_date '{activation_date_str}' for loan ID {loan_id}. Skipping.")
            continue

        if datetime.now() - activation_date > timedelta(days=days_active_for_minimal_payment_check):
            current_balance = get_loan_balance(loan_id)

            if current_balance is None: # Loan might have been deleted or error in get_loan_balance
                print(f"Could not retrieve balance for loan ID {loan_id}. Skipping delinquency check.")
                continue

            amount_paid = principal - current_balance

            # Ensure principal is not zero to avoid DivisionByZeroError
            if principal == 0:
                # If principal is 0, this logic might not apply or needs special handling.
                # For now, assume 0 principal means it's not delinquent by this check if amount_paid is also 0.
                if amount_paid == 0: # Paid 0 on a 0 principal loan, not delinquent by this rule
                    continue
                else: # Paid something on a 0 principal, or negative payment, unusual.
                    print(f"Loan ID {loan_id} has 0 principal but amount_paid is {amount_paid}. Review.")
                    continue


            paid_percentage = amount_paid / principal

            if paid_percentage < principal_paid_percentage_threshold:
                print(f"Loan ID {loan_id} identified as potentially delinquent. "
                      f"Activated: {activation_date_str}, Principal: {principal}, "
                      f"Amount Paid: {amount_paid:.2f}, Paid Percentage: {paid_percentage:.2%}")
                loan['reason_for_delinquency_check'] = (
                    f"Paid {paid_percentage:.2%} of principal after "
                    f"{(datetime.now() - activation_date).days} days. "
                    f"Threshold: {principal_paid_percentage_threshold:.2%}"
                )
                delinquent_loans.append(loan)
        else:
            # Loan is not yet old enough for this specific check
            pass

    return delinquent_loans
