import datetime

class LoanApplication:
    def __init__(self, applicant_name: str, loan_amount: float, purpose: str,
                 application_date_str: str = None, id: int = None, status: str = 'Pending'):
        """
        Represents a loan application.

        Args:
            applicant_name (str): Name of the applicant.
            loan_amount (float): Amount requested for the loan.
            purpose (str): Purpose of the loan.
            application_date_str (str, optional): ISO format string of the application date.
                                                 If None, current datetime is used.
            id (int, optional): Unique ID of the application (usually from database).
            status (str, optional): Current status of the application. Defaults to 'Pending'.
        """
        self.id = id
        self.applicant_name = applicant_name
        self.loan_amount = loan_amount
        self.purpose = purpose
        if application_date_str:
            self.application_date = datetime.datetime.fromisoformat(application_date_str)
        else:
            self.application_date = datetime.datetime.now()
        self.status = status

    def __repr__(self):
        return (f"<LoanApplication(id={self.id}, name='{self.applicant_name}', "
                f"amount={self.loan_amount}, status='{self.status}')>")
