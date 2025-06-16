import unittest
import os
import sqlite3
import datetime # Not strictly needed for these tests yet, but good for consistency
from loan_management_system.database import db_setup
from loan_management_system.servicing.functions import record_payment, get_payments_for_loan, get_loan_balance, activate_loan, get_loan_by_id
from loan_management_system.origination.functions import create_loan_application
from loan_management_system.underwriting.functions import assess_application # assess_application to approve before activating

class TestServicing(unittest.TestCase):
    TEST_DB_NAME = "test_servicing_loan_system.db"
    original_db_name = None
    test_db_path = None

    @classmethod
    def setUpClass(cls):
        cls.original_db_name = db_setup.DATABASE_NAME
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cls.test_db_path = os.path.join(script_dir, cls.TEST_DB_NAME)
        # db_setup.DATABASE_NAME = cls.test_db_path # Set in setUp

    @classmethod
    def tearDownClass(cls):
        if cls.original_db_name:
            db_setup.DATABASE_NAME = cls.original_db_name
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

    def setUp(self):
        db_setup.DATABASE_NAME = self.test_db_path # Ensure test DB is used for each test
        db_setup.create_tables()
        conn = None
        try:
            conn = db_setup.get_db_connection()
            cursor = conn.cursor()
            # Clear all relevant tables before each test
            cursor.execute("DELETE FROM payments")
            cursor.execute("DELETE FROM loans")
            cursor.execute("DELETE FROM loan_applications")
            conn.commit()
        except sqlite3.Error as e:
            self.fail(f"DB setup failed in setUp: {e}")
        finally:
            if conn:
                conn.close()

    def _create_test_loan(self, principal=5000.0, applicant_name="Test Applicant Servicing") -> int | None:
        """Helper method to create an application, approve it, and activate a loan."""
        app_id = create_loan_application(applicant_name, principal, "Test Loan for Servicing")
        if app_id is None: self.fail("_create_test_loan: Failed to create application")

        # Approve the application
        approved = assess_application(app_id, loan_amount_threshold=principal + 1000) # Ensure it's approved
        if not approved: self.fail(f"_create_test_loan: Application {app_id} was not approved.")

        # Activate the loan
        loan_id = activate_loan(application_id=app_id, principal_amount=principal, interest_rate=0.05, term=12)
        if loan_id is None: self.fail("_create_test_loan: Failed to activate loan")
        return loan_id

    def test_record_payment(self):
        loan_id = self._create_test_loan()
        self.assertIsNotNone(loan_id, "Helper _create_test_loan failed to return a loan_id")

        payment_id = record_payment(loan_id, 500.0)
        self.assertIsNotNone(payment_id, "record_payment should return a payment_id")
        self.assertIsInstance(payment_id, int)

        payments = get_payments_for_loan(loan_id)
        self.assertEqual(len(payments), 1, "Should be one payment recorded")
        self.assertEqual(payments[0]['amount_paid'], 500.0)
        self.assertEqual(payments[0]['loan_id'], loan_id)

    def test_record_payment_invalid_loan(self):
        # record_payment should return None if sqlite3.IntegrityError (FK constraint) occurs.
        # The function itself prints an error but doesn't raise.
        payment_id = record_payment(99999, 100.0) # Non-existent loan_id
        self.assertIsNone(payment_id, "payment_id should be None for non-existent loan_id")

    def test_record_payment_negative_amount(self):
        loan_id = self._create_test_loan()
        self.assertIsNotNone(loan_id)
        payment_id = record_payment(loan_id, -100.0)
        self.assertIsNone(payment_id, "payment_id should be None for negative payment amount")

    def test_get_payments_for_loan(self):
        loan_id = self._create_test_loan()
        self.assertIsNotNone(loan_id)
        record_payment(loan_id, 100.0)
        record_payment(loan_id, 200.0)

        payments = get_payments_for_loan(loan_id)
        self.assertEqual(len(payments), 2, "Should retrieve two payments")
        # Payments are ordered by date by default (which is insert order here)
        self.assertEqual(payments[0]['amount_paid'], 100.0)
        self.assertEqual(payments[1]['amount_paid'], 200.0)

    def test_get_payments_for_loan_none_exist(self):
        loan_id = self._create_test_loan()
        self.assertIsNotNone(loan_id)
        payments = get_payments_for_loan(loan_id)
        self.assertEqual(len(payments), 0, "Should return an empty list if no payments exist")

    def test_get_loan_balance(self):
        principal = 5000.0
        loan_id = self._create_test_loan(principal=principal)
        self.assertIsNotNone(loan_id)

        record_payment(loan_id, 500.0)
        record_payment(loan_id, 1000.0)

        balance = get_loan_balance(loan_id)
        self.assertIsNotNone(balance, "Balance should not be None for an existing loan")
        self.assertEqual(balance, principal - 500.0 - 1000.0)

    def test_get_loan_balance_no_payments(self):
        principal = 5000.0
        loan_id = self._create_test_loan(principal=principal)
        self.assertIsNotNone(loan_id)

        balance = get_loan_balance(loan_id)
        self.assertIsNotNone(balance)
        self.assertEqual(balance, principal)

    def test_get_loan_balance_loan_not_found(self):
        balance = get_loan_balance(99999) # Non-existent loan ID
        self.assertIsNone(balance, "Balance should be None for a non-existent loan")

if __name__ == '__main__':
    unittest.main()
