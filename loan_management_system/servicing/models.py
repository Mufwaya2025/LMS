import datetime

class Loan:
    def __init__(self, application_id: int, principal: float, interest_rate: float,
                 term: int, status: str, id: int = None,
                 activation_date_str: str = None, payment_history: list = None):
        """
        Represents a loan.

        Args:
            application_id (int): ID of the associated loan application.
            principal (float): The principal amount of the loan.
            interest_rate (float): The annual interest rate (e.g., 0.05 for 5%).
            term (int): The loan term, typically in months.
            status (str): Current status of the loan (e.g., 'Active', 'Paid Off', 'Defaulted').
            id (int, optional): Unique ID of the loan (usually from database).
            activation_date_str (str, optional): ISO format string of the loan activation date.
                                                If None, current datetime is used.
            payment_history (list, optional): A list of payment records. Defaults to an empty list.
        """
        self.id = id
        self.application_id = application_id
        self.principal = principal
        self.interest_rate = interest_rate
        self.term = term
        self.status = status

        if activation_date_str:
            self.activation_date = datetime.datetime.fromisoformat(activation_date_str)
        else:
            # If no activation date string is provided, it might mean the loan isn't active yet,
            # or we default to now. For a newly created "Active" loan, 'now' makes sense.
            # For loading from DB, this string should always be present if status is 'Active'.
            self.activation_date = datetime.datetime.now()

        self.payment_history = payment_history if payment_history is not None else []

    def __repr__(self):
        return (f"<Loan(id={self.id}, application_id={self.application_id}, "
                f"principal={self.principal}, status='{self.status}')>")
