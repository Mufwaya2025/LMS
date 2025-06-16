class Loan:
    def __init__(self, loan_id, applicant_info, principal, interest_rate, term):
        self.loan_id = loan_id
        self.applicant_info = applicant_info
        self.principal = principal
        self.interest_rate = interest_rate
        self.term = term
        self.status = "Pending Approval"
        self.payment_history = []
