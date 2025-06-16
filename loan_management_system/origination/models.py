import datetime

class LoanApplication:
    def __init__(self, applicant_name, loan_amount, purpose):
        self.applicant_name = applicant_name
        self.loan_amount = loan_amount
        self.purpose = purpose
        self.application_date = datetime.datetime.now()
