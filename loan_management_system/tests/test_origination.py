import unittest
import sqlite3
import os
import datetime
from loan_management_system.origination.functions import create_loan_application, get_loan_application_by_id
from loan_management_system.origination.models import LoanApplication
from loan_management_system.database import db_setup # Import the module itself

class TestOrigination(unittest.TestCase):
    TEST_DB_NAME = 'test_loan_system.db'
    original_db_name = None

    @classmethod
    def setUpClass(cls):
        """
        Store the original database name before any tests run.
        This ensures that even if tests are run multiple times or in parallel (though unittest is serial by default),
        we correctly capture the original state once.
        """
        cls.original_db_name = db_setup.DATABASE_NAME
        # Determine path for test_db relative to this test file's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cls.test_db_path = os.path.join(script_dir, cls.TEST_DB_NAME)


    @classmethod
    def tearDownClass(cls):
        """
        Restore the original database name after all tests in the class have run.
        """
        if cls.original_db_name:
            db_setup.DATABASE_NAME = cls.original_db_name
        # Clean up the test database file if it exists after all tests
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

    def setUp(self):
        """
        Set up a clean test database for each test.
        """
        # Override DATABASE_NAME in db_setup to use the test database path
        db_setup.DATABASE_NAME = self.test_db_path

        # Ensure tables are created in the test_db
        db_setup.create_tables()

        # Clean data from tables before each test
        conn = None
        try:
            conn = db_setup.get_db_connection() # This will now use self.test_db_path
            cursor = conn.cursor()
            cursor.execute("DELETE FROM loan_applications")
            cursor.execute("DELETE FROM loans") # Also clear loans if it's used by these tests or related ones
            conn.commit()
        except sqlite3.Error as e:
            self.fail(f"Database setup failed: {e}")
        finally:
            if conn:
                conn.close()

    def tearDown(self):
        """
        Clean up by removing the test database file after each test.
        The actual restoration of db_setup.DATABASE_NAME is handled in tearDownClass,
        but individual test DB files are removed here to ensure isolation if needed,
        though typically setUpClass/tearDownClass handles shared test DB well.
        For true isolation per test, db creation/deletion would be here.
        Let's keep it simple: create in setUp, clear tables, and tearDownClass removes the file.
        If a test fails, the DB file might remain, which can be useful for debugging.
        The main cleanup is in tearDownClass.
        """
        # No specific action here if tearDownClass handles final DB removal
        pass


    def test_create_loan_application(self):
        applicant_name = "Jane Doe"
        loan_amount = 15000.0
        purpose = "Car Loan"

        app_id = create_loan_application(applicant_name, loan_amount, purpose)

        self.assertIsNotNone(app_id)
        self.assertIsInstance(app_id, int)

        retrieved_app_dict = get_loan_application_by_id(app_id)

        self.assertIsNotNone(retrieved_app_dict)
        self.assertEqual(retrieved_app_dict['applicant_name'], applicant_name)
        self.assertEqual(retrieved_app_dict['loan_amount'], loan_amount)
        self.assertEqual(retrieved_app_dict['purpose'], purpose)
        self.assertEqual(retrieved_app_dict['status'], 'Pending')
        self.assertIn('application_date', retrieved_app_dict)
        # Check application_date is a valid ISO format string and recent
        try:
            date_obj = datetime.datetime.fromisoformat(retrieved_app_dict['application_date'])
            time_difference = datetime.datetime.now() - date_obj
            self.assertTrue(time_difference.total_seconds() < 10) # Allow a bit more leeway
        except ValueError:
            self.fail("Application date is not a valid ISO format string.")

    def test_get_loan_application_by_id_not_found(self):
        retrieved_app = get_loan_application_by_id(99999) # A non-existent ID
        self.assertIsNone(retrieved_app)

    def test_get_loan_application_by_id_successful_retrieval(self):
        # Setup: Directly insert a test record
        conn = None
        app_id = None
        test_applicant_name = "Test User"
        test_loan_amount = 500.0
        test_purpose = "Gadget"
        test_app_date_str = "2023-01-01T10:00:00"
        test_status = "Approved"

        try:
            conn = db_setup.get_db_connection() # Uses test DB
            cursor = conn.cursor()
            sql = "INSERT INTO loan_applications (applicant_name, loan_amount, purpose, application_date, status) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(sql, (test_applicant_name, test_loan_amount, test_purpose, test_app_date_str, test_status))
            app_id = cursor.lastrowid
            conn.commit()
        except sqlite3.Error as e:
            self.fail(f"DB insert failed for test setup: {e}")
        finally:
            if conn:
                conn.close()

        self.assertIsNotNone(app_id, "Setup failed to insert application")

        # Test: Retrieve the application
        retrieved_app_dict = get_loan_application_by_id(app_id)

        self.assertIsNotNone(retrieved_app_dict)
        self.assertEqual(retrieved_app_dict['id'], app_id)
        self.assertEqual(retrieved_app_dict['applicant_name'], test_applicant_name)
        self.assertEqual(retrieved_app_dict['loan_amount'], test_loan_amount)
        self.assertEqual(retrieved_app_dict['purpose'], test_purpose)
        self.assertEqual(retrieved_app_dict['application_date'], test_app_date_str)
        self.assertEqual(retrieved_app_dict['status'], test_status)


if __name__ == '__main__':
    unittest.main()
