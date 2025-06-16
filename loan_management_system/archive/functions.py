from loan_management_system.collection.functions import update_loan_status

# Define statuses that are considered final and suitable for archival.
# This list can be expanded as needed.
ALLOWED_ARCHIVAL_STATUSES = [
    "Archived-PaidOff",
    "Archived-WrittenOff",
    "Archived-Closed",
    "Archived-Rejected" # e.g. if an application was rejected and then archived
]

def archive_loan(loan_id: int, final_status: str) -> bool:
    """
    Archives a loan by updating its status to a designated final/archival status.

    Args:
        loan_id (int): The ID of the loan to be archived.
        final_status (str): The specific archival status to set for the loan.
                            Must be one of ALLOWED_ARCHIVAL_STATUSES.

    Returns:
        bool: True if the loan was successfully archived (status updated), False otherwise.
    """
    if final_status not in ALLOWED_ARCHIVAL_STATUSES:
        print(f"Error: Status '{final_status}' is not a valid archival status. "
              f"Allowed statuses are: {ALLOWED_ARCHIVAL_STATUSES}")
        return False

    print(f"Attempting to archive loan ID {loan_id} with status '{final_status}'...")

    # update_loan_status returns True if rowcount > 0, False otherwise or on error.
    success = update_loan_status(loan_id, final_status)

    if success:
        print(f"Loan ID {loan_id} successfully archived with status '{final_status}'.")
    else:
        # update_loan_status already prints error messages for DB issues or if loan not found/status unchanged.
        print(f"Failed to archive loan ID {loan_id} with status '{final_status}'. See previous messages from update_loan_status.")

    return success
