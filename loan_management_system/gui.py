import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sys
import os

# Ensure the project root is in sys.path for consistent module resolution
# This allows running `python loan_management_system/gui.py` from the /app directory.
if os.path.dirname(os.path.abspath(__file__)) not in sys.path and \
   os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path :
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loan_management_system.database import db_setup

class LoanAppGUI:
    def __init__(self, root_tk):
        self.root = root_tk
        self.root.title("Loan Management System")
        self.root.geometry("800x600") # Initial size

        # --- Database Initialization ---
        # Determine the intended directory for the database (loan_management_system/database/)
        # __file__ is loan_management_system/gui.py
        # db_dir is loan_management_system/database/
        script_dir = os.path.dirname(os.path.abspath(__file__)) # This is /app/loan_management_system
        # To make db_path relative to project root /app, not script_dir
        project_root = os.path.dirname(script_dir) # This should be /app

        db_path = os.path.join(project_root, "loan_management_system", "database", "loan_system.db")

        # Ensure the database directory exists
        db_dir_for_creation = os.path.dirname(db_path)
        if not os.path.exists(db_dir_for_creation):
            os.makedirs(db_dir_for_creation)
            print(f"Created database directory: {db_dir_for_creation}")

        db_setup.DATABASE_NAME = db_path
        print(f"GUI using DB at: {db_path}") # For debugging
        db_setup.create_tables() # Ensures DB and tables are ready

        # Create Menu Bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Application", command=self.placeholder_command) # Placeholder for now
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # (Optional) Edit/View Menus
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Placeholder", command=self.placeholder_command)

        # Add a simple label to indicate the GUI is running
        main_label = ttk.Label(self.root, text="Loan Management System GUI - Welcome!", font=("Arial", 16))
        main_label.pack(pady=20)

    def placeholder_command(self):
        messagebox.showinfo("Placeholder", "This feature is not yet implemented.")

if __name__ == '__main__':
    root = tk.Tk()
    app = LoanAppGUI(root)
    root.mainloop()
