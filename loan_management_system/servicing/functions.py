from .models import Loan
from loan_management_system.origination.models import LoanApplication

active_loans = []

def activate_loan(application: LoanApplication, loan_id: str, interest_rate: float, term: int) -> Loan:
    """
    Activates a loan based on an approved application.
    """
    loan = Loan(
        loan_id=loan_id,
        applicant_info=application, # Storing the whole application object for now
        principal=application.loan_amount,
        interest_rate=interest_rate,
        term=term
    )
    loan.status = "Active"
    active_loans.append(loan)
    return loan
