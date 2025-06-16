from loan_management_system.servicing.functions import list_all_loans
from loan_management_system.origination.functions import list_all_applications

def generate_active_loans_report() -> list[dict]:
    """
    Generates a report of all active loans.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents an active loan.
    """
    print("Generating active loans report...")
    active_loans = list_all_loans(status_filter='Active')
    print(f"Found {len(active_loans)} active loans.")
    return active_loans

def generate_application_status_report() -> list[dict]:
    """
    Generates a report of all loan applications and their statuses.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents a loan application.
    """
    print("Generating application status report...")
    all_applications = list_all_applications() # Gets all applications regardless of status
    print(f"Found {len(all_applications)} applications in total.")

    # Optional: Group by status if desired for a more structured report
    # applications_by_status = {}
    # for app in all_applications:
    #     status = app.get('status', 'Unknown')
    #     if status not in applications_by_status:
    #         applications_by_status[status] = []
    #     applications_by_status[status].append(app)
    # return applications_by_status # This would change the return type

    return all_applications
