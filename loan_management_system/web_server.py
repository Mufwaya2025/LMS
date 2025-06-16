import http.server
import socketserver
import urllib.parse
import os
import sys
import json # For potential future JSON responses

# Ensure the project root is in sys.path for consistent module resolution
project_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root_dir not in sys.path:
    sys.path.append(project_root_dir)

from loan_management_system.database import db_setup
from loan_management_system.origination.functions import list_all_applications, create_loan_application, get_loan_application_by_id
from loan_management_system.servicing.functions import list_all_loans # Added for dashboard
from loan_management_system.underwriting.functions import assess_application # For linking, not direct use in GET
# Add more imports as needed for other functionalities
from .html_utils import generate_page_header, generate_page_footer, generate_table, generate_form, generate_alert_message


def initialize_database():
    """Initializes the database and ensures tables are created."""
    # Path to the database file, located in loan_management_system/database/loan_system.db
    # __file__ is /app/loan_management_system/web_server.py
    # script_dir is /app/loan_management_system
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # db_dir should be /app/loan_management_system/database/
    db_dir = os.path.join(script_dir, "database")

    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"Created database directory: {db_dir}")

    db_path = os.path.join(db_dir, "loan_system.db")

    db_setup.DATABASE_NAME = db_path
    print(f"Web server using DB at: {db_path}")
    db_setup.create_tables()

class LoanManagementHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Custom HTTP request handler for the Loan Management System.
    Serves dynamic content for specific paths and static files otherwise (if needed).
    """

    # Override to prevent serving files from the directory by default if not intended
    # For now, we only handle specific GET paths.
    # If you want to serve static files (CSS, JS), you might adjust SimpleHTTPRequestHandler's directory.

    def do_GET(self):
        """Handles GET requests."""
        parsed_path = urllib.parse.urlparse(self.path)
        path_components = parsed_path.path.strip('/').split('/')
        query_params = urllib.parse.parse_qs(parsed_path.query)

        response_code = 200
        html_body_content = "" # Initialize body content

        page_title = "Loan Management System" # Default title

        if (path_components[0] == '' and len(path_components) == 1) or path_components[0] == 'index.html': # Root path
            page_title = "Welcome - Loan Management System"
            html_body_content = "<h2>Welcome to the Loan Management System!</h2>"
            html_body_content += "<p>Use the navigation menu to manage loans and applications.</p>"

            # Quick Summary/Dashboard
            try:
                all_apps = list_all_applications()
                all_loans = list_all_loans()

                active_loan_count = sum(1 for loan in all_loans if loan.get('status') == 'Active')
                pending_app_count = sum(1 for app in all_apps if app.get('status') == 'Pending')

                html_body_content += "<h3>System Summary:</h3><ul>"
                html_body_content += f"<li>Total Loan Applications Logged: {len(all_apps)}</li>"
                html_body_content += f"<li>Total Loans Activated: {len(all_loans)}</li>"
                html_body_content += f"<li>Active Loans: {active_loan_count}</li>"
                html_body_content += f"<li>Pending Applications: {pending_app_count}</li>"
                html_body_content += "</ul>"
            except Exception as e:
                print(f"Error generating dashboard summary: {e}")
                html_body_content += generate_alert_message("Could not load system summary.", "error")

        elif path_components[0] == 'applications':
            page_title = "Loan Applications - LMS"
            current_filter_value = query_params.get('status_filter', [''])[0]

            # Filter form
            filter_form_fields = [
                {'label': 'Filter by Status', 'name': 'status_filter', 'type': 'text', 'value': current_filter_value}
            ]
            filter_form_html = generate_form(action="/applications", method="GET", fields=filter_form_fields, submit_text="Filter")

            html_body_content = "<h2>Loan Applications</h2>" + filter_form_html

            # Modify backend call for filtering
            status_value_to_filter = current_filter_value if current_filter_value.strip() else None
            apps = list_all_applications(status_filter=status_value_to_filter)

            headers = ["ID", "Applicant Name", "Loan Amount", "Purpose", "Application Date", "Status", "Actions"]
            rows = []
            if apps: # Ensure apps is not None before iterating
                for app in apps:
                    app_id = app.get('id', 'N/A')
                    # Add link to detail view for ID
                    id_link = f"<a href='/application/details?id={app_id}'>{app_id}</a>"
                    # Add more action links if needed, e.g., assess
                    action_links = f"<a href='/application/details?id={app_id}'>View Details</a>"

                    rows.append([
                        id_link, # ID is now a link
                        app.get('applicant_name', 'N/A'),
                        f"{app.get('loan_amount', 0):.2f}",
                        app.get('purpose', 'N/A'),
                        app.get('application_date', 'N/A'),
                        app.get('status', 'N/A'),
                        action_links # Actions cell
                    ])
            html_body_content += generate_table(headers, rows)

        elif path_components[0] == 'application' and len(path_components) > 1 and path_components[1] == 'details':
            app_id_str = query_params.get('id', [None])[0]
            page_title = "Application Details - LMS" # Default before knowing app_id

            # Check for messages from POST redirect
            assessed_param = query_params.get('assessed', [None])[0]
            created_param = query_params.get('created', [None])[0]
            error_param = query_params.get('error', [None])[0] # For other errors like invalid_threshold

            if assessed_param == 'true':
                result_param = query_params.get('result', [''])[0]
                message = f"Application assessment result: {result_param.capitalize()}."
                msg_type = "success" if result_param == "approved" else "error"
                html_body_content += generate_alert_message(message, msg_type)
            elif created_param == 'true':
                html_body_content += generate_alert_message("Application successfully created!", "success")
            elif error_param == 'invalid_threshold': # This error is specific to assessment
                html_body_content += generate_alert_message("Assessment failed: Invalid threshold value provided.", "error")
            # Can add more specific error checks here based on query_params from redirects for other actions

            if not app_id_str:
                html_body_content += generate_alert_message("Application ID not provided.", "error")
                page_title = "Error - LMS"
            else:
                try:
                    app_id = int(app_id_str)
                    page_title = f"Application Details - ID: {app_id}" # Update title with actual ID
                    app_data = get_loan_application_by_id(app_id)

                    if not app_data:
                        # If an alert for 'assessed' was already added, this might be redundant or could be combined.
                        # For now, it's fine, it will show both.
                        html_body_content = generate_alert_message(f"Application with ID {app_id} not found.", "error")
                    else:
                        html_body_content = f"<h2>Application Details (ID: {app_id})</h2>"
                        details_html = "<ul>"
                        for key, value in app_data.items():
                            formatted_value = f"{value:.2f}" if isinstance(value, float) and key == 'loan_amount' else value
                            details_html += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {formatted_value}</li>"
                        details_html += "</ul>"
                        html_body_content += details_html

                        html_body_content += "<hr><h3>Actions:</h3>"

                        # Assess Application Form (if status is Pending)
                        if app_data.get('status') == 'Pending':
                            assess_form_fields = [
                                {'name': 'application_id', 'type': 'hidden', 'value': app_id},
                                {'label': 'Assessment Threshold', 'name': 'threshold', 'type': 'number', 'step': 'any', 'placeholder': 'e.g., 20000 (optional)'}
                            ]
                            html_body_content += "<h4>Assess Application</h4>"
                            html_body_content += generate_form(action="/assess_application_action", method="POST", fields=assess_form_fields, submit_text="Assess")

                        # Activate Loan Form (if status is Approved)
                        elif app_data.get('status') == 'Approved':
                            activate_form_fields = [
                                {'name': 'application_id', 'type': 'hidden', 'value': app_id},
                                {'label': 'Principal', 'name': 'principal', 'type': 'number', 'step': 'any', 'value': app_data.get('loan_amount', 0.0), 'required': True},
                                {'label': 'Interest Rate (e.g., 0.05)', 'name': 'interest_rate', 'type': 'number', 'step': '0.001', 'required': True},
                                {'label': 'Term (months)', 'name': 'term', 'type': 'number', 'required': True}
                            ]
                            html_body_content += "<h4>Activate Loan</h4>"
                            html_body_content += generate_form(action="/activate_loan_action", method="POST", fields=activate_form_fields, submit_text="Activate Loan")
                        else:
                            html_body_content += f"<p>No further actions available for status: {app_data.get('status')}.</p>"

                        html_body_content += f"<hr><p><a href='/applications'>&laquo; Back to Applications List</a></p>"

                except ValueError:
                    page_title = "Error - LMS"
                    html_body_content = generate_alert_message("Invalid Application ID format. ID must be an integer.", "error")

        elif path_components[0] == 'create_application_form':
            page_title = "Create New Loan Application - Loan Management System"
            html_body_content = "" # Initialize

            # Check for error messages from POST redirect
            error_param = query_params.get('error', [None])[0]
            if error_param == 'missing_fields':
                html_body_content += generate_alert_message("All fields are required. Please fill out the entire form.", "error")
            elif error_param == 'invalid_amount':
                html_body_content += generate_alert_message("Loan amount must be a valid positive number.", "error")
            elif error_param == 'creation_failed':
                html_body_content += generate_alert_message("Failed to create application due to a server error. Please try again.", "error")

            html_body_content += "<h2>Create New Loan Application</h2>"
            html_body_content += "<p>Please fill out the details below to apply for a new loan.</p>"

            form_fields = [
                {'label': 'Applicant Name', 'name': 'applicant_name', 'type': 'text', 'required': True},
                {'label': 'Loan Amount', 'name': 'loan_amount', 'type': 'number', 'step': '0.01', 'required': True, 'placeholder': 'e.g., 10000.00'},
                {'label': 'Purpose of Loan', 'name': 'purpose', 'type': 'textarea', 'required': True, 'placeholder': 'e.g., Home renovation, car purchase, etc.'}
            ]
            # The action URL will be /create_application_action; a POST handler will be added for it.
            html_body_content += generate_form(action="/create_application_action", method="POST", fields=form_fields, submit_text="Submit Application")

        # Add a placeholder for /loans page
        elif path_components[0] == 'loans':
            page_title = "View Loans - Loan Management System"
            current_filter_value = query_params.get('status_filter', [''])[0]

            filter_form_fields = [
                {'label': 'Filter by Status', 'name': 'status_filter', 'type': 'text', 'value': current_filter_value}
            ]
            filter_form_html = generate_form(action="/loans", method="GET", fields=filter_form_fields, submit_text="Filter")
            html_body_content = "<h2>View Loans</h2>" + filter_form_html

            status_value_to_filter = current_filter_value if current_filter_value.strip() else None
            loans = list_all_loans(status_filter=status_value_to_filter) # Ensure list_all_loans is imported

            if loans:
                headers = ["ID", "App ID", "Principal", "Interest Rate", "Term (Months)", "Status", "Activation Date", "Actions"]
                rows_data = []
                for loan in loans:
                    loan_id = loan.get('id', 'N/A')
                    interest_rate_display = f"{loan.get('interest_rate', 0) * 100:.2f}%"
                    # Link to a future /loan/details page
                    actions_link = f"<a href='/loan/details?id={loan_id}'>View Details</a>"

                    rows_data.append([
                        loan_id,
                        loan.get('application_id', 'N/A'),
                        f"{loan.get('principal', 0):.2f}",
                        interest_rate_display,
                        loan.get('term', 'N/A'),
                        loan.get('status', 'N/A'),
                        loan.get('activation_date', 'N/A'),
                        actions_link
                    ])
                html_body_content += generate_table(headers, rows_data)
            else:
                html_body_content += generate_alert_message(f"No loans found{(f' with status {status_value_to_filter}' if status_value_to_filter else '')}.", "info")

        else:
            response_code = 404
            page_title = "Error - LMS"
            html_body_content = "<h2>Page Not Found</h2><p>The requested page does not exist.</p>"

        # Assemble the full page using utility functions
        full_html_output = generate_page_header(title=page_title) + html_body_content + generate_page_footer()

        self.send_response(response_code)
        self.send_header("Content-type", "text/html; charset=utf-8") # Ensure UTF-8 for broader character support
        self.end_headers()
        self.wfile.write(full_html_output.encode('utf-8'))

    def do_POST(self):
        """Handles POST requests."""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        content_length = int(self.headers.get('Content-Length', 0))
        post_data_bytes = self.rfile.read(content_length)
        post_data_str = post_data_bytes.decode('utf-8')
        form_params = urllib.parse.parse_qs(post_data_str)

        if path == '/assess_application_action':
            application_id_str = form_params.get('application_id', [None])[0]
            threshold_str = form_params.get('threshold', [None])[0]

            if not application_id_str:
                self.send_error(400, "Bad Request: Missing application_id")
                return

            try:
                application_id = int(application_id_str)
            except ValueError:
                self.send_error(400, "Bad Request: Invalid application_id format")
                return

            assessment_args = {'application_id': application_id}

            if threshold_str and threshold_str.strip():
                try:
                    assessment_args['loan_amount_threshold'] = float(threshold_str)
                except ValueError:
                    # Option 1: Redirect with error message
                    self.send_response(302)
                    self.send_header('Location', f'/application/details?id={application_id}&error=invalid_threshold')
                    self.end_headers()
                    return
                    # Option 2: Send error page (less ideal for POST-redirect-GET)
                    # self.send_error(400, "Bad Request: Invalid threshold format")
                    # return

            # Call the backend function
            # assess_application returns True if approved, False if rejected or error
            # It also prints its own logs.
            approved = assess_application(**assessment_args)

            # Redirect back to the application detail page with a result message
            self.send_response(302)
            redirect_url = f'/application/details?id={application_id}&assessed=true&result={"approved" if approved else "rejected"}'
            # If assess_application itself returned False because app_id was not found by its internal get_loan_application_by_id
            # we might want a different result. However, assess_application returns False for "not found" too.
            # The get_application_status on the detail page will show the updated status.

            # Check if app exists after assessment attempt to refine message (optional)
            # current_app_status = get_loan_application_by_id(application_id) # Assuming this returns dict or None
            # if not current_app_status :
            #    redirect_url = f'/application/details?id={application_id}&error=app_not_found_post_assessment'

            self.send_header('Location', redirect_url)
            self.end_headers()

        elif path == '/create_application_action':
            applicant_name = form_params.get('applicant_name', [''])[0].strip()
            loan_amount_str = form_params.get('loan_amount', [''])[0].strip()
            purpose = form_params.get('purpose', [''])[0].strip()

            error_redirect_url = '/create_application_form?error='

            if not applicant_name or not loan_amount_str or not purpose:
                self.send_response(302)
                self.send_header('Location', error_redirect_url + 'missing_fields')
                self.end_headers()
                return

            try:
                loan_amount = float(loan_amount_str)
                if loan_amount <= 0:
                    raise ValueError("Loan amount must be positive.")
            except ValueError:
                self.send_response(302)
                self.send_header('Location', error_redirect_url + 'invalid_amount')
                self.end_headers()
                return

            # If validation passes:
            app_id = create_loan_application(applicant_name, loan_amount, purpose) # Ensure create_loan_application is imported

            if app_id is not None:
                self.send_response(302)
                self.send_header('Location', f'/application/details?id={app_id}&created=true')
                self.end_headers()
            else:
                self.send_response(302)
                self.send_header('Location', error_redirect_url + 'creation_failed')
                self.end_headers()

        # Placeholder for other POST actions like activate_loan_action
        # elif path == '/activate_loan_action':
            # ... similar logic ...

        else:
            self.send_error(404, "POST path not found")


if __name__ == '__main__':
    PORT = 8000

    # Initialize the database (ensures tables exist and correct DB path is used)
    initialize_database()

    Handler = LoanManagementHTTPRequestHandler

    # Use ThreadingHTTPServer for basic multi-threading capability
    # http.server.TCPServer is single-threaded.
    try:
        # Try importing ThreadingHTTPServer, fallback to TCPServer if not available (older Python versions)
        from http.server import ThreadingHTTPServer
        httpd_server_type = ThreadingHTTPServer
    except ImportError:
        httpd_server_type = socketserver.TCPServer # or http.server.TCPServer

    with httpd_server_type(("", PORT), Handler) as httpd:
        print(f"Serving Loan Management System on http://localhost:{PORT}")
        print("Open your browser and navigate to the address above.")
        print("Press Ctrl+C to stop the server.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown() # Ensure clean shutdown
            print("Server stopped.")
            sys.exit(0)
        except Exception as e:
            print(f"Server error: {e}")
            httpd.shutdown()
            sys.exit(1)
