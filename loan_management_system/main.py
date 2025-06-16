import argparse
import sys
import os


from loan_management_system.origination import functions as orig_funcs
from loan_management_system.underwriting import functions as under_funcs
from loan_management_system.servicing import functions as serv_funcs
from loan_management_system.collection import functions as coll_funcs
from loan_management_system.reports import functions as report_funcs
from loan_management_system.archive import functions as archive_funcs
from loan_management_system.database import db_setup

def main():
    # --- Database Path Setup ---
    # Determine the intended directory for the database (loan_management_system/database/)
    # __file__ is loan_management_system/main.py
    # db_dir is loan_management_system/database/
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database")
    if not os.path.exists(db_dir):
        os.makedirs(db_dir) # Create database directory if it doesn't exist

    actual_db_path = os.path.join(db_dir, "loan_system.db")

    # Override the DATABASE_NAME in db_setup before any function uses it.
    # This ensures the database is consistently located in loan_management_system/database/
    db_setup.DATABASE_NAME = actual_db_path
    # print(f"CLI using DB at: {actual_db_path}") # For debugging

    # Ensure tables exist in the correctly located DB
    # This will also ensure PRAGMA foreign_keys=ON is set for subsequent connections.
    db_setup.create_tables()


    parser = argparse.ArgumentParser(description="Loan Management System CLI")
    subparsers = parser.add_subparsers(dest='command', title='commands', help='Available commands')
    if sys.version_info >= (3, 7): # 'required' появился в 3.7
        subparsers.required = True


    # --- (Future: Add more subparsers for origination, underwriting, etc.) ---
    # Example structure for modular commands (can be built out in next steps)

    # --- Origination Commands ---
    orig_cli_parser = subparsers.add_parser('origination', help='Loan origination commands')
    orig_cli_subparsers = orig_cli_parser.add_subparsers(dest='orig_command', title='origination_commands')
    if sys.version_info >= (3,7): orig_cli_subparsers.required = True

    create_app_parser = orig_cli_subparsers.add_parser('create-application', help='Create a new loan application')
    create_app_parser.add_argument('--name', type=str, required=True, help="Applicant's name")
    create_app_parser.add_argument('--amount', type=float, required=True, help="Loan amount requested")
    create_app_parser.add_argument('--purpose', type=str, required=True, help="Purpose of the loan")

    list_apps_parser = orig_cli_subparsers.add_parser('list-applications', help='List loan applications') # Moved here
    list_apps_parser.add_argument('--status', type=str, help='Filter applications by status (e.g., Pending, Approved, Rejected)')

    get_app_parser = orig_cli_subparsers.add_parser('get-application', help='Get a specific loan application by ID')
    get_app_parser.add_argument('--id', type=int, required=True, help="Application ID")


    # --- Underwriting Commands ---
    under_parser = subparsers.add_parser('underwriting', help='Loan underwriting commands')
    under_subparsers = under_parser.add_subparsers(dest='under_command', title='underwriting_commands')
    if sys.version_info >= (3,7): under_subparsers.required = True

    assess_app_parser = under_subparsers.add_parser('assess-application', help='Assess a loan application')
    assess_app_parser.add_argument('--id', type=int, required=True, help="Application ID to assess")
    assess_app_parser.add_argument('--threshold', type=float, help="Loan amount approval threshold (optional, defaults to backend default)")

    get_status_parser = under_subparsers.add_parser('get-application-status', help="Get an application's status")
    get_status_parser.add_argument('--id', type=int, required=True, help="Application ID")


    # --- Servicing Commands ---
    serv_parser = subparsers.add_parser('servicing', help='Loan servicing commands')
    serv_subparsers = serv_parser.add_subparsers(dest='serv_command', title='servicing_commands')
    if sys.version_info >= (3,7): serv_subparsers.required = True

    activate_loan_parser = serv_subparsers.add_parser('activate-loan', help='Activate a loan from an approved application')
    activate_loan_parser.add_argument('--app-id', type=int, required=True, help='ID of the approved loan application')
    activate_loan_parser.add_argument('--principal', type=float, required=True, help='Principal loan amount (should match application)')
    activate_loan_parser.add_argument('--rate', type=float, required=True, help='Annual interest rate (e.g., 0.05 for 5%)')
    activate_loan_parser.add_argument('--term', type=int, required=True, help='Loan term in months')

    get_loan_parser = serv_subparsers.add_parser('get-loan', help='Get details of a loan')
    get_loan_parser.add_argument('--id', type=int, required=True, help='Loan ID')

    record_payment_parser = serv_subparsers.add_parser('record-payment', help='Record a payment for a loan')
    record_payment_parser.add_argument('--loan-id', type=int, required=True, help="Loan ID")
    record_payment_parser.add_argument('--amount', type=float, required=True, help="Payment amount")

    get_payments_parser = serv_subparsers.add_parser('get-payments', help='Get payment history for a loan')
    get_payments_parser.add_argument('--loan-id', type=int, required=True, help="Loan ID")

    get_balance_parser = serv_subparsers.add_parser('get-balance', help='Get the current balance of a loan')
    get_balance_parser.add_argument('--loan-id', type=int, required=True, help="Loan ID")

    list_loans_parser = serv_subparsers.add_parser('list-loans', help='List all loans')
    list_loans_parser.add_argument('--status', type=str, help='Filter loans by status (e.g., Active, PaidOff)')


    # --- Collection Commands ---
    coll_parser = subparsers.add_parser('collection', help='Loan collection commands')
    coll_subparsers = coll_parser.add_subparsers(dest='collection_command', title='collection_commands')
    if sys.version_info >= (3,7): coll_subparsers.required = True

    update_status_parser = coll_subparsers.add_parser('update-loan-status', help='Update the status of a loan')
    update_status_parser.add_argument('--loan-id', type=int, required=True, help="Loan ID")
    update_status_parser.add_argument('--new-status', type=str, required=True, help="The new status for the loan (e.g., In Collection, Defaulted)")

    identify_delinquent_parser = coll_subparsers.add_parser('identify-delinquent', help='Identify potentially delinquent loans (basic placeholder logic)')
    identify_delinquent_parser.add_argument('--days-active', type=int, help='Minimum days loan has been active (optional, defaults to backend default)')
    identify_delinquent_parser.add_argument('--paid-ratio', type=float, help='Minimum principal paid ratio threshold (e.g., 0.1 for 10%) (optional, defaults to backend default)')


    # --- Reports Commands ---
    reports_parser = subparsers.add_parser('reports', help='Reporting actions')
    reports_subparsers = reports_parser.add_subparsers(dest='reports_command', title='reports_commands')
    if sys.version_info >= (3,7): reports_subparsers.required = True

    report_active_loans_parser = reports_subparsers.add_parser('active-loans', help='Generate a report of all active loans')
    report_app_statuses_parser = reports_subparsers.add_parser('application-statuses', help='Generate a report of all application statuses')


    # --- Archive Commands ---
    archive_parser = subparsers.add_parser('archive', help='Archive actions')
    archive_subparsers = archive_parser.add_subparsers(dest='archive_command', title='archive_commands')
    if sys.version_info >= (3,7): archive_subparsers.required = True

    archive_loan_parser = archive_subparsers.add_parser('archive-loan', help='Archive a loan with a final status')
    archive_loan_parser.add_argument('--loan-id', type=int, required=True, help="Loan ID to archive")
    archive_loan_parser.add_argument('--final-status', type=str, required=True,
                                     help=f"Final status (e.g., {archive_funcs.ALLOWED_ARCHIVAL_STATUSES})")


    args = parser.parse_args()

    # Command Handlers
    if args.command == 'origination':
        if args.orig_command == 'create-application':
            app_id = orig_funcs.create_loan_application(
                applicant_name=args.name,
                loan_amount=args.amount,
                purpose=args.purpose
            )
            if app_id is not None:
                print(f"Loan application created successfully. Application ID: {app_id}")
            else:
                print("Failed to create loan application. Check logs for database errors.")

        elif args.orig_command == 'list-applications':
            # print(f"Attempting to list applications with status filter: {args.status}") # Debug print
            apps = orig_funcs.list_all_applications(status_filter=args.status)
            if apps:
                print(f"\n--- Loan Applications ({args.status if args.status else 'All'}) ---")
                for app in apps:
                    print(f"  ID: {app['id']}, Name: {app['applicant_name']}, Amount: {app['loan_amount']:.2f}, "
                          f"Purpose: {app['purpose']}, Date: {app['application_date']}, Status: {app['status']}")
                print("-----------------------------------------")
            else:
                print(f"No applications found{(f' with status {args.status}' if args.status else '')}.")

        elif args.orig_command == 'get-application':
            app_data = orig_funcs.get_loan_application_by_id(args.id)
            if app_data:
                print("\n--- Loan Application Details ---")
                for key, value in app_data.items():
                    # Format amount if it's a float, otherwise print as is
                    if isinstance(value, float):
                        print(f"  {key.replace('_', ' ').title()}: {value:.2f}")
                    else:
                        print(f"  {key.replace('_', ' ').title()}: {value}")
                print("------------------------------")
            else:
                print(f"Application with ID {args.id} not found.")

    elif args.command == 'underwriting':
        if args.under_command == 'assess-application':
            # The assess_application function prints details of the assessment process
            # and returns True for Approved, False for Rejected/Not Found/Error
            if args.threshold is not None:
                approved = under_funcs.assess_application(args.id, loan_amount_threshold=args.threshold)
            else:
                approved = under_funcs.assess_application(args.id) # Uses default threshold from function

            # assess_application prints its own messages like:
            # "Application ID X assessed. Decision: Y. Status updated in DB."
            # or "Application with ID X not found for assessment."
            # or "Database error..."
            # The CLI can provide a slightly different summary or confirmation.
            final_status_after_assessment = under_funcs.get_application_status(args.id) # Check status after attempt
            if final_status_after_assessment:
                print(f"CLI: Application ID {args.id} processed. Current status: {final_status_after_assessment}.")
                if approved: # This 'approved' is the direct boolean return from assess_application
                     print(f"CLI: Assessment function indicates: Approved.")
                else:
                     # This covers Rejected, or if assess_application returned False due to app not found or DB error
                     print(f"CLI: Assessment function indicates: Not Approved (e.g. Rejected, application not found, or DB error during update).")
            else:
                 # This means the application was not found by assess_application OR get_application_status post-attempt
                 print(f"CLI: Application ID {args.id} could not be found or processed.")

        elif args.under_command == 'get-application-status':
            status = under_funcs.get_application_status(args.id)
            if status:
                print(f"Status for application ID {args.id}: {status}")
            else:
                print(f"Could not retrieve status for application ID {args.id} (application may not exist).")

    elif args.command == 'servicing':
        if args.serv_command == 'activate-loan':
            # Check application status before activating
            app_status = under_funcs.get_application_status(args.app_id)
            if app_status == "Approved":
                # Verify principal matches application amount (optional good practice, not strictly required by subtask)
                app_details = orig_funcs.get_loan_application_by_id(args.app_id)
                if app_details and app_details['loan_amount'] != args.principal:
                    print(f"Warning: Principal amount {args.principal} does not match approved application amount {app_details['loan_amount']}.")
                    # Decide if this should prevent activation or just warn. For now, proceed.

                loan_id = serv_funcs.activate_loan(
                    application_id=args.app_id,
                    principal_amount=args.principal,
                    interest_rate=args.rate,
                    term=args.term
                )
                if loan_id is not None:
                    print(f"Loan activated successfully. Loan ID: {loan_id}")
                else:
                    print(f"Failed to activate loan for application ID {args.app_id}.")
            else:
                print(f"Cannot activate loan. Application ID {args.app_id} status is '{app_status}' (must be 'Approved').")

        elif args.serv_command == 'get-loan':
            loan_data = serv_funcs.get_loan_by_id(args.id)
            if loan_data:
                print("\n--- Loan Details ---")
                for key, value in loan_data.items():
                    if key in ['principal', 'interest_rate'] and isinstance(value, (float, int)):
                        print(f"  {key.replace('_', ' ').title()}: {value:.2f}" + ("%" if 'rate' in key else ""))
                    else:
                        print(f"  {key.replace('_', ' ').title()}: {value}")
                print("--------------------")
            else:
                print(f"Loan with ID {args.id} not found.")

        elif args.serv_command == 'record-payment':
            payment_id = serv_funcs.record_payment(args.loan_id, args.amount)
            # record_payment prints its own success/failure messages related to DB interaction
            if payment_id:
                print(f"CLI: Payment recorded successfully. Payment ID: {payment_id}")
            else:
                print(f"CLI: Failed to record payment for loan ID {args.loan_id}. See previous error messages.")

        elif args.serv_command == 'get-payments':
            payments = serv_funcs.get_payments_for_loan(args.loan_id)
            if payments:
                print(f"\n--- Payments for Loan ID {args.loan_id} ---")
                for pmt in payments:
                    print(f"  ID: {pmt['id']}, Date: {pmt['payment_date']}, Amount: {pmt['amount_paid']:.2f}")
                print("------------------------------------")
            else:
                print(f"No payments found for loan ID {args.loan_id}.")

        elif args.serv_command == 'get-balance':
            balance = serv_funcs.get_loan_balance(args.loan_id)
            if balance is not None:
                print(f"Current balance for loan ID {args.loan_id}: {balance:.2f}")
            else:
                # get_loan_balance prints "Loan with ID X not found..." or "Principal amount not found..."
                print(f"CLI: Could not retrieve balance for loan ID {args.loan_id}.")

        elif args.serv_command == 'list-loans':
            loans = serv_funcs.list_all_loans(status_filter=args.status)
            if loans:
                print(f"\n--- Loans ({args.status if args.status else 'All'}) ---")
                for loan in loans:
                    print(f"  ID: {loan['id']}, App ID: {loan['application_id']}, Principal: {loan['principal']:.2f}, "
                          f"Rate: {loan['interest_rate']:.2%}, Term: {loan['term']}m, " # Assuming rate is stored as decimal e.g. 0.05
                          f"Activation: {loan['activation_date']}, Status: {loan['status']}")
                print("-----------------------------------------")
            else:
                print(f"No loans found{(f' with status {args.status}' if args.status else '')}.")

    elif args.command == 'collection':
        if args.collection_command == 'update-loan-status':
            success = coll_funcs.update_loan_status(args.loan_id, args.new_status)
            # coll_funcs.update_loan_status prints its own detailed messages
            if success:
                print(f"CLI: Loan ID {args.loan_id} status update process completed successfully to '{args.new_status}'.")
            else:
                print(f"CLI: Failed to update status for loan ID {args.loan_id}. See previous messages for details.")

        elif args.collection_command == 'identify-delinquent':
            kwargs = {}
            if args.days_active is not None:
                kwargs['days_active_for_minimal_payment_check'] = args.days_active
            if args.paid_ratio is not None:
                kwargs['principal_paid_percentage_threshold'] = args.paid_ratio

            # The backend function prints details during its check
            delinquent_loans = coll_funcs.identify_delinquent_loans(**kwargs)

            if delinquent_loans:
                print("\n--- CLI: Potentially Delinquent Loans Identified ---")
                for loan in delinquent_loans:
                    # Assuming identify_delinquent_loans returns a list of dicts (the loan dicts)
                    # and might add a 'reason_for_delinquency_check' key to them.
                    print(f"  Loan ID: {loan.get('id')}, "
                          f"App ID: {loan.get('application_id')}, "
                          f"Principal: {loan.get('principal', 0):.2f}, "
                          f"Status: {loan.get('status')}")
                    if 'reason_for_delinquency_check' in loan:
                         print(f"    Reason: {loan['reason_for_delinquency_check']}")
                print("----------------------------------------------------")
            else:
                print("CLI: No loans identified as potentially delinquent based on the provided criteria.")

    elif args.command == 'reports':
        if args.reports_command == 'active-loans':
            active_loans = report_funcs.generate_active_loans_report()
            # generate_active_loans_report already prints a line like "Found X active loans."
            if active_loans:
                print("\n--- CLI: Active Loans Report ---")
                for loan in active_loans:
                    print(f"  ID: {loan.get('id')}, App ID: {loan.get('application_id')}, "
                          f"Principal: {loan.get('principal', 0):.2f}, "
                          f"Interest Rate: {loan.get('interest_rate', 0):.2%}, " # Assuming rate is decimal
                          f"Term: {loan.get('term')}m, Status: {loan.get('status')}, "
                          f"Activation: {loan.get('activation_date')}")
                print(f"--- End of Report ({len(active_loans)} loan(s)) ---")
            else:
                print("CLI: No active loans found to report.")

        elif args.reports_command == 'application-statuses':
            applications = report_funcs.generate_application_status_report()
            # generate_application_status_report already prints "Found X applications..."
            if applications:
                print("\n--- CLI: Application Statuses Report ---")
                for app in applications:
                    print(f"  ID: {app.get('id')}, Name: {app.get('applicant_name')}, "
                          f"Amount: {app.get('loan_amount', 0):.2f}, "
                          f"Status: {app.get('status')}, Date: {app.get('application_date')}")
                print(f"--- End of Report ({len(applications)} application(s)) ---")
            else:
                print("CLI: No applications found to report.")

    elif args.command == 'archive':
        if args.archive_command == 'archive-loan':
            success = archive_funcs.archive_loan(args.loan_id, args.final_status)
            # archive_funcs.archive_loan prints detailed messages about status validity and DB update results.
            if success:
                print(f"CLI: Loan ID {args.loan_id} archival process to status '{args.final_status}' reported success.")
            else:
                print(f"CLI: Loan ID {args.loan_id} archival process failed. "
                      f"Check previous messages for details (e.g., invalid status, loan not found). "
                      f"Valid statuses are: {archive_funcs.ALLOWED_ARCHIVAL_STATUSES}")


    else:
        # This case should ideally not be reached if subparsers are required.
        print(f"Unknown or unimplemented command: {args.command}")

if __name__ == '__main__':
    main()
