from .models import LoanApplication

loan_applications = []

def create_loan_application(applicant_name: str, loan_amount: float, purpose: str) -> LoanApplication:
    """
    Creates a new loan application and stores it.
    """
    application = LoanApplication(
        applicant_name=applicant_name,
        loan_amount=loan_amount,
        purpose=purpose
    )
    loan_applications.append(application)
    return application
