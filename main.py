import pandas as pd
import csv
from datetime import datetime
from data_entry import CATEGORIES, get_Amount, get_Category, get_Date, get_Description
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class FinanceTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Finance Tracker")
        self.geometry("800x600")
        self.configure(bg='white')

        # Create UI components
        self.create_widgets()

    def create_widgets(self):
        # Create buttons
        add_button = tk.Button(self, text="Add Transaction", command=self.add_transaction_window)
        view_button = tk.Button(self, text="View Transactions", command=self.view_transactions_window)
        exit_button = tk.Button(self, text="Exit", command=self.quit)

        # Layout buttons
        add_button.pack(pady=10)
        view_button.pack(pady=10)
        exit_button.pack(pady=10)

    def add_transaction_window(self):
        window = tk.Toplevel(self)
        window.title("Add Transaction")
        window.geometry("400x300")
        window.configure(bg='white')

        # Date entry
        tk.Label(window, text="Date (dd-mm-yyyy):").pack(pady=5)
        date_entry = tk.Entry(window)
        date_entry.pack(pady=5)
        date_entry.insert(0, datetime.today().strftime("%d-%m-%Y"))

        # Amount entry
        tk.Label(window, text="Amount:").pack(pady=5)
        amount_entry = tk.Entry(window)
        amount_entry.pack(pady=5)

        # Category entry
        tk.Label(window, text="Category ('I' for Income, 'E' for Expense):").pack(pady=5)
        category_entry = tk.Entry(window)
        category_entry.pack(pady=5)

        # Description entry
        tk.Label(window, text="Description:").pack(pady=5)
        description_entry = tk.Entry(window)
        description_entry.pack(pady=5)

        # Add button
        def on_add():
            date = date_entry.get()
            try:
                amount = float(amount_entry.get())
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid amount.")
                return

            category = category_entry.get().upper()
            if category not in CATEGORIES:
                messagebox.showerror("Invalid Input", "Please enter 'I' for Income or 'E' for Expense.")
                return

            description = description_entry.get()

            CSV.add_entry(date, amount, CATEGORIES[category], description)
            messagebox.showinfo("Success", "Transaction added successfully!")
            window.destroy()

        tk.Button(window, text="Add", command=on_add).pack(pady=20)

    def view_transactions_window(self):
        window = tk.Toplevel(self)
        window.title("View Transactions")
        window.geometry("800x600")
        window.configure(bg='white')

        # Start and end date entries
        tk.Label(window, text="Start Date (dd-mm-yyyy):").pack(pady=5)
        start_date_entry = tk.Entry(window)
        start_date_entry.pack(pady=5)

        tk.Label(window, text="End Date (dd-mm-yyyy):").pack(pady=5)
        end_date_entry = tk.Entry(window)
        end_date_entry.pack(pady=5)

        # View button
        def on_view():
            start_date = start_date_entry.get()
            end_date = end_date_entry.get()
            df = CSV.get_transactions(start_date, end_date)

            if not df.empty:
                self.show_transaction_summary(window, df)
                
                # Display transactions
                transactions_text = tk.Text(window, wrap='word', bg='white', font=("Arial", 10))
                transactions_text.pack(pady=10, fill=tk.BOTH, expand=True)

                transactions_str = df.to_string(index=False, columns=CSV.COLUMNS)
                transactions_text.insert(tk.END, transactions_str)

                # Ask for plot
                if messagebox.askyesno("Plot", "Do you want to see a plot?"):
                    self.plot_transactions_window(df)

        tk.Button(window, text="View", command=on_view).pack(pady=20)

    def show_transaction_summary(self, parent, df):
        total_income = df[df["Category"] == "Income"]["Amount"].sum()
        total_expense = df[df["Category"] == "Expense"]["Amount"].sum()
        net_savings = total_income - total_expense

        summary_text = (
            f"Total Income: FCFA {total_income:.2f}\n"
            f"Total Expense: FCFA {total_expense:.2f}\n"
            f"Net Savings: FCFA {net_savings:.2f}"
        )

        summary_label = tk.Label(parent, text=summary_text, bg='white', font=("Arial", 12))
        summary_label.pack(pady=10)

    def plot_transactions_window(self, df):
        window = tk.Toplevel(self)
        window.title("Transactions Plot")
        window.geometry("800x600")

        df.set_index("Date", inplace=True)
        income_df = df[df["Category"] == "Income"].resample("D").sum().reindex(df.index, fill_value=0)
        expense_df = df[df["Category"] == "Expense"].resample("D").sum().reindex(df.index, fill_value=0)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(income_df.index, income_df["Amount"], label="Income", color='b')
        ax.plot(expense_df.index, expense_df["Amount"], label="Expense", color='r')
        ax.set_xlabel("Date")
        ax.set_ylabel("Amount")
        ax.set_title("Incomes & Expenses over time")
        ax.legend()
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Add save button
        def save_plot():
            fig.savefig('transactions_plot.png')
            messagebox.showinfo("Saved", "Plot saved as 'transactions_plot.png'.")

        save_button = tk.Button(window, text="Save Plot", command=save_plot)
        save_button.pack(pady=10)

class CSV:
    csv_file = "finance_data.csv"
    COLUMNS = ["Date", "Amount", "Category", "Description"]
    FORMAT = "%d-%m-%Y"

    @classmethod
    def initialize_csv(cls):
        try:
            pd.read_csv(cls.csv_file)
        except FileNotFoundError:
            df = pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.csv_file, index=False)

    @classmethod
    def add_entry(cls, date, amount, category, description):
        new_entry = {
            "Date": date,
            "Amount": amount,
            "Category": category,
            "Description": description
        }
        with open(cls.csv_file, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)
        print("Entry added successfully")

    @classmethod
    def get_transactions(cls, start_date, end_date):
        df = pd.read_csv(cls.csv_file)
        df["Date"] = pd.to_datetime(df["Date"], format=CSV.FORMAT)
        start_date = datetime.strptime(start_date, CSV.FORMAT)
        end_date = datetime.strptime(end_date, CSV.FORMAT)

        mask = (df["Date"] >= start_date) & (df["Date"] <= end_date)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            messagebox.showinfo("No Transactions", 'No transactions found in the given range.')
        else:
            messagebox.showinfo("Transactions", f'Transactions from {start_date.strftime(CSV.FORMAT)} to {end_date.strftime(CSV.FORMAT)}')

        return filtered_df

if __name__ == "__main__":
    CSV.initialize_csv()
    app = FinanceTrackerApp()
    app.mainloop()
