import unittest
import os
import sqlite3
from loan_management_system.database import db_setup # Import the module itself
from loan_management_system.underwriting.functions import assess_application, get_application_status
from loan_management_system.origination.functions import create_loan_application, get_loan_application_by_id

class TestUnderwriting(unittest.TestCase):
    TEST_DB_NAME = "test_underwriting_loan_system.db"
    original_db_name = None
    test_db_path = None

    @classmethod
    def setUpClass(cls):
        cls.original_db_name = db_setup.DATABASE_NAME
        # Place test DB in the same directory as this test file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cls.test_db_path = os.path.join(script_dir, cls.TEST_DB_NAME)
        db_setup.DATABASE_NAME = cls.test_db_path
        # Create tables once for the class if they are not schema-version dependent per test
        # db_setup.create_tables() # Usually called in setUp for per-test clean state

    @classmethod
    def tearDownClass(cls):
        if cls.original_db_name:
            db_setup.DATABASE_NAME = cls.original_db_name
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

    def setUp(self):
        # Ensure DATABASE_NAME is set to test path for each test, as it might be reset by other test classes
        db_setup.DATABASE_NAME = self.test_db_path
        db_setup.create_tables() # Create tables fresh for each test for isolation
        conn = None
        try:
            conn = db_setup.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM loan_applications")
            cursor.execute("DELETE FROM loans") # Though not directly used, good practice
            # cursor.execute("DELETE FROM payments") # If payments table is involved
            conn.commit()
        except sqlite3.Error as e:
            self.fail(f"DB setup failed in setUp: {e}")
        finally:
            if conn:
                conn.close()

    def test_assess_application_approve(self):
        app_id = create_loan_application("Test Approve", 10000.0, "Holiday")
        self.assertIsNotNone(app_id, "Failed to create application for approval test")

        approved = assess_application(app_id, loan_amount_threshold=20000.0)
        self.assertTrue(approved, "Application should have been approved")

        status = get_application_status(app_id)
        self.assertEqual(status, "Approved", "Application status in DB is not 'Approved'")

    def test_assess_application_reject(self):
        app_id = create_loan_application("Test Reject", 30000.0, "Big Holiday")
        self.assertIsNotNone(app_id, "Failed to create application for rejection test")

        approved = assess_application(app_id, loan_amount_threshold=20000.0)
        self.assertFalse(approved, "Application should have been rejected")

        status = get_application_status(app_id)
        self.assertEqual(status, "Rejected", "Application status in DB is not 'Rejected'")

    def test_assess_application_not_found(self):
        # assess_application prints an error and returns False if app not found
        approved = assess_application(99999)
        self.assertFalse(approved, "assess_application should return False for a non-existent application ID")

    def test_get_application_status(self):
        app_id = create_loan_application("Test Status Check", 5000.0, "Gadgets")
        self.assertIsNotNone(app_id, "Failed to create application for status check test")

        # Initial status should be 'Pending'
        status_before_assessment = get_application_status(app_id)
        self.assertEqual(status_before_assessment, "Pending", "Initial status should be 'Pending'")

        assess_application(app_id, loan_amount_threshold=10000.0) # Should approve

        status_after_assessment = get_application_status(app_id)
        self.assertEqual(status_after_assessment, "Approved", "Status after approval assessment is incorrect")

    def test_get_application_status_not_found(self):
        status = get_application_status(88888)
        self.assertIsNone(status, "get_application_status should return None for non-existent application")

if __name__ == '__main__':
    unittest.main()
