import unittest
import datetime # Required for LoanApplication's application_date
from loan_management_system.origination.functions import create_loan_application, loan_applications
from loan_management_system.origination.models import LoanApplication

class TestOrigination(unittest.TestCase):

    def tearDown(self):
        """
        Clean up after each test.
        """
        loan_applications.clear()

    def test_create_loan_application(self):
        applicant_name = "John Doe"
        loan_amount = 10000.0
        purpose = "Home Improvement"

        application = create_loan_application(applicant_name, loan_amount, purpose)

        self.assertIsInstance(application, LoanApplication)
        self.assertEqual(application.applicant_name, applicant_name)
        self.assertEqual(application.loan_amount, loan_amount)
        self.assertEqual(application.purpose, purpose)
        self.assertIn(application, loan_applications)
        self.assertTrue(len(loan_applications) == 1)

        # Check application_date is recent (e.g., within the last 5 seconds)
        # This can be a bit flaky, but good for a basic check.
        time_difference = datetime.datetime.now() - application.application_date
        self.assertTrue(time_difference.total_seconds() < 5)


if __name__ == '__main__':
    unittest.main()
