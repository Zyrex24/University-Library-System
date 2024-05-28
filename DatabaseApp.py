import pyodbc
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class DatabaseApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Online Library Website")
        self.master.configure(bg='#AFD3E2')

        self.server = 'Zyrex\\SQLEXPRESS'
        self.database = 'library'
        self.username = 'sa'
        self.password = 'AsAs1234'

        # Connect to SQL Server
        self.conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + self.server + ';DATABASE=' + self.database + ';UID='
            + self.username + ';PWD=' + self.password)
        self.cursor = self.conn.cursor()

        # Load and display the logo
        self.logo_image = tk.PhotoImage(file="OnlineLibrary1.png")  # Update with your logo path
        self.logo_label = tk.Label(master, image=self.logo_image, bg='#AFD3E2')
        self.logo_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Table selection dropdown
        self.table_label = tk.Label(master, text="Select Table:", bg='#AFD3E2')
        self.table_label.grid(row=1, column=0, padx=10, pady=10)
        self.tables = ['Admin', 'libraryuser', 'Author', 'Publisher', 'Book', 'Chapter', 'Borrow', 'BookAuthor']
        self.selected_table = tk.StringVar()
        self.table_menu = ttk.Combobox(master, textvariable=self.selected_table, values=self.tables)
        self.table_menu.grid(row=1, column=1, padx=10, pady=10)
        self.table_menu.current(0)  # Set default selection

        # Action selection dropdown
        self.action_label = tk.Label(master, text="Select Action:", bg='#AFD3E2')
        self.action_label.grid(row=2, column=0, padx=10, pady=10)
        self.actions = ['Insert', 'Update', 'Delete', 'Select', 'Select with Join']
        self.selected_action = tk.StringVar()
        self.action_menu = ttk.Combobox(master, textvariable=self.selected_action, values=self.actions)
        self.action_menu.grid(row=2, column=1, padx=10, pady=10)
        self.action_menu.current(0)  # Set default selection

        # Entry widgets for values
        self.entry_widgets = {}

        # Button to generate report
        self.report_button = tk.Button(master, text="Generate Report", command=self.generate_report)
        self.report_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Text widget to display results
        self.result_text = tk.Text(master, height=10, width=100)  # Adjusted width for better fit
        self.result_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Button for executing action
        self.action_button = tk.Button(master, text="Execute Action", command=self.execute_action)
        self.action_button.grid(row=20, column=0, columnspan=2, padx=10, pady=10)

        # Bind combobox selection to update fields
        self.table_menu.bind("<<ComboboxSelected>>", self.update_fields)
        self.action_menu.bind("<<ComboboxSelected>>", self.update_fields)

        # Join selections (initially hidden)
        self.join_table_label = tk.Label(master, text="Select Table to Join:", bg='#AFD3E2')
        self.join_tables = ttk.Combobox(master, values=self.tables)
        self.checkbox_label = tk.Label(master, text="Select Columns:", bg='#AFD3E2')
        self.select_all_var = tk.BooleanVar()
        self.select_all_checkbox = tk.Checkbutton(master, text="Select All", variable=self.select_all_var,
                                                  command=self.select_all_columns, bg='#AFD3E2')

        # Variable to store column checkboxes
        self.column_vars = {}

        # Initially update fields based on default selection
        self.update_fields(None)

    def update_fields(self, event):
        # Remove existing entry widgets
        for widget in self.entry_widgets.values():
            widget[0].grid_forget()
            widget[1].grid_forget()

        # Clear the entry_widgets dictionary
        self.entry_widgets = {}

        # Remove existing checkboxes
        for var in self.column_vars.values():
            var[0].grid_forget()

        # Clear the column_vars dictionary
        self.column_vars = {}

        # Hide join related fields initially
        self.join_table_label.grid_forget()
        self.join_tables.grid_forget()
        self.checkbox_label.grid_forget()
        self.select_all_checkbox.grid_forget()

        # Get selected table
        table = self.selected_table.get()

        # Get column names for selected table
        column_names = self.get_column_names(table)

        # Create entry widgets for column names based on action
        action = self.selected_action.get()

        if action in ['Insert', 'Update', 'Delete']:
            for i, column_name in enumerate(column_names):
                label = tk.Label(self.master, text=column_name, bg='#AFD3E2')
                entry = tk.Entry(self.master)
                label.grid(row=i + 6, column=0, padx=10, pady=5)
                entry.grid(row=i + 6, column=1, padx=10, pady=5)
                self.entry_widgets[column_name] = (label, entry)
        elif action == 'Select':
            # Create checkboxes for column selection
            self.checkbox_label.grid(row=5, column=0, padx=10, pady=5, columnspan=2)
            self.select_all_checkbox.grid(row=6, column=0, padx=10, pady=5, columnspan=2)
            for i, column_name in enumerate(column_names):
                var = tk.BooleanVar()
                chk = tk.Checkbutton(self.master, text=column_name, variable=var, bg='#AFD3E2')
                chk.grid(row=i + 7, column=0, columnspan=2, padx=10, pady=5)
                self.column_vars[column_name] = (chk, var)
        elif action == 'Select with Join':
            # Show "Select Table to Join" dropdown
            self.join_table_label.grid(row=5, column=0, padx=10, pady=10)
            self.join_tables.grid(row=5, column=1, padx=10, pady=10)
            self.checkbox_label.grid(row=6, column=0, padx=10, pady=5, columnspan=2)
            self.select_all_checkbox.grid(row=7, column=0, padx=10, pady=5, columnspan=2)

            # Create checkboxes for column selection from the main table
            for i, column_name in enumerate(column_names):
                var = tk.BooleanVar()
                chk = tk.Checkbutton(self.master, text=column_name, variable=var, bg='#AFD3E2')
                chk.grid(row=i + 7, column=0, padx=10, pady=5)
                self.column_vars[table + '.' + column_name] = (chk, var)

            # Bind the selected table event to update join column checkboxes
            self.join_tables.bind("<<ComboboxSelected>>", self.update_join_columns)

    def update_join_columns(self, event):
        # Remove existing join table checkboxes
        try:
            for var in self.column_vars.values():
                if var[0].grid_info().get("column") == 1:
                    var[0].grid_forget()

            # Get selected join table
            join_table = self.join_tables.get()

            # Get column names for the selected join table
            join_column_names = self.get_column_names(join_table)

            # Create checkboxes for column selection from the join table
            for i, column_name in enumerate(join_column_names):
                var = tk.BooleanVar()
                chk = tk.Checkbutton(self.master, text=column_name, variable=var, bg='#AFD3E2')
                chk.grid(row=i + 7, column=1, padx=10, pady=5)
                self.column_vars[join_table + '.' + column_name] = (chk, var)
        except KeyError as e:
            messagebox.showerror("Join Error", "Error: These two tables cannot be joined.")

    def get_column_names(self, table):
        # Query to get column names of the table
        query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}'"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        column_names = [row[0] for row in rows]
        return column_names

    def execute_query(self, query):
        self.cursor.execute(query)
        self.conn.commit()

    def execute_action(self):
        table = self.selected_table.get()
        action = self.selected_action.get()
        values = {label: entry.get() for label, (label_widget, entry) in self.entry_widgets.items()}

        try:
            if action == 'Insert':
                columns = ', '.join(values.keys())
                vals = "', '".join(values.values())
                query = f"INSERT INTO {table} ({columns}) VALUES ('{vals}')"
            elif action == 'Update':
                set_clause = ', '.join([f"{col}='{val}'" for col, val in values.items()])
                query = f"UPDATE {table} SET {set_clause} WHERE {next(iter(values))}='{next(iter(values.values()))}'"
            elif action == 'Delete':
                where_clause = ' AND '.join([f"{col}='{val}'" for col, val in values.items()])
                query = f"DELETE FROM {table} WHERE {where_clause}"
            elif action == 'Select':
                selected_columns = [col for col, var in self.column_vars.items() if var[1].get()]
                columns = ', '.join(selected_columns) if selected_columns else '*'
                query = f"SELECT {columns} FROM {table}"
                self.cursor.execute(query)
                rows = self.cursor.fetchall()
                self.display_results(rows)
                return
            elif action == 'Select with Join':
                join_table = self.join_tables.get()
                if not join_table:
                    messagebox.showerror("Error", "Please select a table to join.")
                    return
                selected_columns = [col for col, var in self.column_vars.items() if var[1].get()]
                if not selected_columns:
                    selected_columns = ['*']

                # Building the column list with table prefixes
                main_table_columns = [f"{table}.{col.split('.')[1]}" for col in selected_columns if
                                      col.startswith(table)]
                join_table_columns = [f"{join_table}.{col.split('.')[1]}" for col in selected_columns if
                                      col.startswith(join_table)]
                all_columns = main_table_columns + join_table_columns
                columns = ', '.join([f"{col} AS [{col.replace('.', '_')}]" for col in all_columns])

                # For simplicity, using CROSS JOIN, but it can be adjusted to other joins (INNER JOIN, LEFT JOIN, etc.)
                query = f"SELECT {columns} FROM {table} CROSS JOIN {join_table}"
                self.cursor.execute(query)
                rows = self.cursor.fetchall()
                self.display_results(rows)
                return

            self.execute_query(query)
            messagebox.showinfo("Success", f"Record {action.lower()}ed successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_results(self, rows):
        self.result_text.delete(1.0, tk.END)
        for row in rows:
            self.result_text.insert(tk.END, str(row) + "\n")

    def select_all_columns(self):
        select_all = self.select_all_var.get()
        for chk, var in self.column_vars.values():
            var.set(select_all)

    def close_connection(self):
        self.conn.close()
        self.master.destroy()

    def get_group_by_report(self):
        table = 'Book'
        group_by_column = 'AuthorName'  # Example column to group by
        query = f"SELECT {group_by_column}, COUNT(*) FROM {table} GROUP BY {group_by_column}"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_last_10_borrowed_books_report(self):
        query = """
        SELECT TOP 10 * FROM Borrow
        ORDER BY BorrowingDate DESC
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_complex_query_report(self):
        query = """
        SELECT b.Title, u.UserName, br.BorrowingDate
        FROM Book b
        JOIN Borrow br ON b.BookID = br.BookID
        JOIN libraryuser u ON br.UserID = u.UserID
        WHERE br.BorrowingDate > DATEADD(month, -1, GETDATE())
        ORDER BY br.BorrowingDate DESC
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def generate_report(self):
        # Get data for each part of the report
        group_by_data = self.get_group_by_report()
        last_10_books_data = self.get_last_10_borrowed_books_report()
        complex_query_data = self.get_complex_query_report()

        # Format the report
        report = "Library Report\n"
        report += "====================\n\n"

        report += "Group By AuthorName\n"
        report += "--------------------\n"
        for row in group_by_data:
            report += f"AuthorName: {row[0]}, Count: {row[1]}\n"
        report += "\n"

        report += "Last 10 Borrowed Books\n"
        report += "--------------------\n"
        for row in last_10_books_data:
            report += f"{row}\n"
        report += "\n"

        report += "Books Borrowed in the Last Month\n"
        report += "--------------------\n"
        for row in complex_query_data:
            report += f"BookTitle: {row[0]}, UserName: {row[1]}, BorrowDate: {row[2]}\n"

        # Display the report in the text widget
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, report)

        # Optionally, save the report to a file
        with open("library_report.txt", "w") as file:
            file.write(report)

        messagebox.showinfo("Report Generated", "The report has been generated and saved to library_report.txt")


if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close_connection)
    root.mainloop()
