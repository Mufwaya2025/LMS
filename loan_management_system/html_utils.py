def generate_page_header(title="Loan Management System"):
    return f"""
    <html><head><title>{title}</title>
    <style>
        body {{ font-family: sans-serif; margin: 20px; background-color: #f4f7f6; color: #333; }}
        nav a {{ margin-right: 15px; text-decoration: none; color: #007bff; }}
        nav a:hover {{ text-decoration: underline; color: #0056b3; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 15px; box-shadow: 0 2px 3px rgba(0,0,0,0.1); }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #007bff; color: white; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .container {{ max-width: 1000px; margin: auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #007bff; border-bottom: 2px solid #007bff; padding-bottom: 10px;}}
        h2 {{ color: #333; }}
        hr {{ border: none; border-top: 1px solid #eee; margin-top: 20px; margin-bottom: 20px; }}
        .alert {{ padding: 15px; margin-bottom:20px; border-radius: 4px; border: 1px solid transparent; }}
        .alert-success {{ background-color: #d4edda; color: #155724; border-color: #c3e6cb; }}
        .alert-error {{ background-color: #f8d7da; color: #721c24; border-color: #f5c6cb; }}
        form p {{ margin-bottom: 10px; }}
        form p label {{ display: inline-block; width: 150px; font-weight: bold; }}
        form p input[type="text"], form p input[type="number"], form p input[type="email"], form p textarea {{
            width: calc(100% - 160px); padding: 8px; border: 1px solid #ccc; border-radius: 4px;
        }}
        form p input[type="submit"] {{
            background-color: #007bff; color: white; padding: 10px 15px; border: none;
            border-radius: 4px; cursor: pointer; font-size: 16px;
        }}
        form p input[type="submit"]:hover {{ background-color: #0056b3; }}
    </style>
    </head><body>
    <div class='container'>
    <h1>{title}</h1>
    <nav>
        <a href="/">Home</a> |
        <a href="/applications">Applications</a> |
        <a href="/loans">Loans</a> |
        <a href="/create_application_form">New Application</a>
        {""}
    </nav>
    <hr>
    """ # Removed "стин" typo

def generate_page_footer():
    current_year = __import__('datetime').datetime.now().year
    return f"""
    <hr>
    <footer>
        <p>&copy; {current_year} Loan Management System. All rights reserved.</p>
    </footer>
    </div></body></html>
    """

def generate_table(headers, rows_data):
    # rows_data is a list of lists, where each inner list is a row
    html = "<table><thead><tr>"
    for header in headers:
        html += f"<th>{header}</th>"
    html += "</tr></thead><tbody>"
    if not rows_data:
        html += f"<tr><td colspan='{len(headers)}' style='text-align:center;'>No data available.</td></tr>"
    else:
        for row in rows_data:
            html += "<tr>"
            for cell in row:
                html += f"<td>{str(cell)}</td>" # Ensure cells are strings
            html += "</tr>"
    html += "</tbody></table>"
    return html

def generate_form(action, method="POST", fields=None, submit_text="Submit"):
    # fields is a list of dicts, e.g., [{'label': 'Name', 'name': 'applicant_name', 'type': 'text', 'required': True}]
    if fields is None: fields = []
    html = f'<form action="{action}" method="{method}">'
    for field in fields:
        label = field.get('label', field['name'].replace('_', ' ').title())
        input_type = field.get('type', 'text')
        name_attr = field["name"] # Corrected: use field["name"] for name attribute
        id_attr = field.get('id', name_attr) # Use name_attr as default for id
        required_attr = "required" if field.get('required', False) else ""
        value_attr = f"value='{field.get('value', '')}'" if 'value' in field and input_type != 'textarea' else ""

        html += f'<p><label for="{id_attr}">{label}:</label> '
        if input_type == 'textarea':
            html += f'<textarea name="{name_attr}" id="{id_attr}" {required_attr}>{field.get("value", "")}</textarea></p>'
        else:
            html += f'<input type="{input_type}" name="{name_attr}" id="{id_attr}" {value_attr} {required_attr}></p>'
    html += f'<p><input type="submit" value="{submit_text}"></p>'
    html += '</form>'
    return html

def generate_alert_message(message, m_type="success"):
    # m_type can be "success" or "error"
    return f'<div class="alert alert-{m_type}">{message}</div>'

# Example usage (optional, for direct testing of this file)
if __name__ == '__main__':
    header = generate_page_header("Test Page")
    footer = generate_page_footer()

    # Test table
    table_headers = ["Name", "Age", "City"]
    table_rows = [
        ["Alice", 30, "New York"],
        ["Bob", 24, "Los Angeles"],
        ["Charlie", 28, "Chicago"]
    ]
    table_html = generate_table(table_headers, table_rows)
    empty_table_html = generate_table(table_headers, [])

    # Test form
    form_fields = [
        {'label': 'Full Name', 'name': 'full_name', 'type': 'text', 'required': True},
        {'label': 'Email Address', 'name': 'email_addr', 'type': 'email', 'value': 'test@example.com'},
        {'label': 'Age', 'name': 'age', 'type': 'number'},
        {'label': 'Comments', 'name': 'comments', 'type': 'textarea', 'required': True}
    ]
    form_html = generate_form("/submit_data", fields=form_fields, submit_text="Register")

    # Test alerts
    success_alert = generate_alert_message("Operation completed successfully!")
    error_alert = generate_alert_message("An error occurred.", m_type="error")

    # Combine and print or save to a file
    full_html = header + \
                "<h2>Test Table</h2>" + table_html + \
                "<h2>Empty Table</h2>" + empty_table_html + \
                "<h2>Test Form</h2>" + form_html + \
                "<h2>Alerts</h2>" + success_alert + error_alert + \
                footer

    # print(full_html) # You can print to console or write to an HTML file
    with open("html_utils_test.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("Generated html_utils_test.html for review.")
