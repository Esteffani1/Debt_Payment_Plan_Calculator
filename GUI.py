import csv
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from Debt_Payment_Calculator_Plan.Debt_entry import DebtEntry, write_debt_entries_to_file
    from Debt_Payment_Calculator_Plan.Snowball_Method import load_and_sort_debts as load_snowball
    from Debt_Payment_Calculator_Plan.Avalanche_Method import load_and_sort_debts as load_avalanche
    from Debt_Payment_Calculator_Plan.Debt_Calculator import simulate_debt_payoff
except ModuleNotFoundError:
    sys.path.insert(0, os.path.dirname(__file__))
    from Debt_entry import DebtEntry, write_debt_entries_to_file
    from Snowball_Method import load_and_sort_debts as load_snowball
    from Avalanche_Method import load_and_sort_debts as load_avalanche
    from Debt_Calculator import simulate_debt_payoff


DEBT_LIST_PATH = os.path.join(os.path.dirname(__file__), "Debt_Payment_Calculator_Plan", "Debt_list.txt")


class DebtPlannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Debt Payment Planner")
        self.root.geometry("850x700")
        self.debts = []
        self.sorted_debts = []
        self.simulation_results = None
        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill="both", expand=True)

        title = ttk.Label(frame, text="Debt Payment Planner", font=("Segoe UI", 18, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=(0, 10), sticky="w")

        self._build_debt_entry_panel(frame)
        self._build_debt_list_panel(frame)
        self._build_strategy_panel(frame)
        self._build_results_panel(frame)

    def _build_debt_entry_panel(self, parent):
        debt_frame = ttk.LabelFrame(parent, text="Add Debt Entry", padding=10)
        debt_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 10))

        ttk.Label(debt_frame, text="Name:").grid(row=0, column=0, sticky="w")
        self.name_entry = ttk.Entry(debt_frame, width=28)
        self.name_entry.grid(row=0, column=1, sticky="w", padx=(4, 12))

        ttk.Label(debt_frame, text="Balance ($):").grid(row=0, column=2, sticky="w")
        self.balance_entry = ttk.Entry(debt_frame, width=16)
        self.balance_entry.grid(row=0, column=3, sticky="w", padx=(4, 12))

        ttk.Label(debt_frame, text="Interest Rate (%):").grid(row=1, column=0, sticky="w")
        self.rate_entry = ttk.Entry(debt_frame, width=16)
        self.rate_entry.grid(row=1, column=1, sticky="w", padx=(4, 12))

        ttk.Label(debt_frame, text="Minimum Payment ($):").grid(row=1, column=2, sticky="w")
        self.minimum_entry = ttk.Entry(debt_frame, width=16)
        self.minimum_entry.grid(row=1, column=3, sticky="w", padx=(4, 12))

        add_button = ttk.Button(debt_frame, text="Add Debt", command=self.add_debt)
        add_button.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        clear_button = ttk.Button(debt_frame, text="Clear All Debts", command=self.clear_debts)
        clear_button.grid(row=2, column=2, columnspan=2, pady=(10, 0), sticky="ew")

    def _build_debt_list_panel(self, parent):
        list_frame = ttk.LabelFrame(parent, text="Current Debt List", padding=10)
        list_frame.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=(0, 10))
        parent.rowconfigure(2, weight=1)

        columns = ("name", "balance", "rate", "minimum")
        self.debt_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        self.debt_tree.heading("name", text="Name")
        self.debt_tree.heading("balance", text="Balance")
        self.debt_tree.heading("rate", text="Interest Rate")
        self.debt_tree.heading("minimum", text="Minimum Payment")
        self.debt_tree.column("name", width=260)
        self.debt_tree.column("balance", width=120, anchor="e")
        self.debt_tree.column("rate", width=120, anchor="e")
        self.debt_tree.column("minimum", width=140, anchor="e")
        self.debt_tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.debt_tree.yview)
        self.debt_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        remove_button = ttk.Button(parent, text="Remove Selected", command=self.remove_selected_debt)
        remove_button.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(0, 10))

    def _build_strategy_panel(self, parent):
        strategy_frame = ttk.LabelFrame(parent, text="Payment Strategy", padding=10)
        strategy_frame.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(0, 10))

        self.method_var = tk.StringVar(value="snowball")
        snowball_radio = ttk.Radiobutton(strategy_frame, text="Snowball", variable=self.method_var, value="snowball")
        avalanche_radio = ttk.Radiobutton(strategy_frame, text="Avalanche", variable=self.method_var, value="avalanche")
        snowball_radio.grid(row=0, column=0, padx=(0, 20))
        avalanche_radio.grid(row=0, column=1, padx=(0, 20))

        ttk.Label(strategy_frame, text="Monthly Budget ($):").grid(row=0, column=2, sticky="w")
        self.budget_entry = ttk.Entry(strategy_frame, width=16)
        self.budget_entry.grid(row=0, column=3, sticky="w", padx=(4, 12))

        calculate_button = ttk.Button(strategy_frame, text="Calculate Payoff", command=self.calculate_payoff)
        calculate_button.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        export_button = ttk.Button(strategy_frame, text="Export Results to CSV", command=self.export_results)
        export_button.grid(row=1, column=2, columnspan=2, pady=(10, 0), sticky="ew")

    def _build_results_panel(self, parent):
        results_frame = ttk.LabelFrame(parent, text="Results", padding=10)
        results_frame.grid(row=5, column=0, columnspan=4, sticky="nsew")
        parent.rowconfigure(5, weight=0)

        self.results_text = tk.Text(results_frame, height=14, wrap="word", state="disabled")
        self.results_text.pack(fill="both", expand=True)

    def add_debt(self):
        name = self.name_entry.get().strip()
        balance = self.balance_entry.get().strip()
        interest_rate = self.rate_entry.get().strip()
        minimum_payment = self.minimum_entry.get().strip()

        if not name:
            messagebox.showerror("Input Error", "Debt name is required.")
            return

        try:
            balance_value = float(balance)
            interest_value = float(interest_rate)
            minimum_value = float(minimum_payment)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values for balance, interest rate, and minimum payment.")
            return

        if balance_value < 0 or minimum_value < 0:
            messagebox.showerror("Input Error", "Balance and minimum payment must be non-negative.")
            return

        if interest_value < 0:
            messagebox.showerror("Input Error", "Interest rate must be non-negative.")
            return

        if interest_value > 1:
            interest_value /= 100.0

        debt = DebtEntry(name, balance_value, interest_value, minimum_value)
        self.debts.append(debt)
        self._refresh_debt_list()
        self._clear_entries()

    def remove_selected_debt(self):
        selected = self.debt_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Choose a debt entry to remove.")
            return
        index = self.debt_tree.index(selected[0])
        self.debts.pop(index)
        self._refresh_debt_list()

    def clear_debts(self):
        if messagebox.askyesno("Clear Debts", "Remove all debts from the list?"):
            self.debts.clear()
            self.sorted_debts.clear()
            self.simulation_results = None
            self._refresh_debt_list()
            self._write_results("Debt list cleared.")

    def _clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.balance_entry.delete(0, tk.END)
        self.rate_entry.delete(0, tk.END)
        self.minimum_entry.delete(0, tk.END)

    def _refresh_debt_list(self):
        for row in self.debt_tree.get_children():
            self.debt_tree.delete(row)
        for debt in self.debts:
            self.debt_tree.insert("", "end", values=(
                debt.name,
                f"${debt.balance:,.2f}",
                f"{debt.interest_rate:.2%}",
                f"${debt.minimum_payment:,.2f}",
            ))

    def calculate_payoff(self):
        if not self.debts:
            messagebox.showerror("No Debt Entries", "Add at least one debt entry before calculating payoff.")
            return

        budget_text = self.budget_entry.get().strip()
        try:
            monthly_budget = float(budget_text)
            if monthly_budget <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Enter a valid monthly budget greater than 0.")
            return

        self._save_debt_list()
        method = self.method_var.get()

        if method == "snowball":
            self.sorted_debts = load_snowball(DEBT_LIST_PATH)
        else:
            self.sorted_debts = load_avalanche(DEBT_LIST_PATH)

        months, total_interest = simulate_debt_payoff(self.sorted_debts, monthly_budget)
        total_debt = sum(debt.balance for debt in self.sorted_debts)
        total_paid = total_debt + total_interest
        years = months // 12
        remaining_months = months % 12

        summary = [
            f"Selected method: {method.capitalize()}",
            f"Monthly budget: ${monthly_budget:,.2f}",
            f"Number of debts: {len(self.sorted_debts)}",
            f"Total debt: ${total_debt:,.2f}",
            "",
            "Payoff summary:",
            f"  Months to pay off: {months} ({years} years and {remaining_months} months)",
            f"  Total interest paid: ${total_interest:,.2f}",
            f"  Total paid: ${total_paid:,.2f}",
            "",
            "Sorted debt order:" 
        ]
        for debt in self.sorted_debts:
            summary.append(f"  {debt.name}: ${debt.balance:,.2f} @ {debt.interest_rate:.2%} (min ${debt.minimum_payment:,.2f})")

        self.simulation_results = {
            "method": method,
            "monthly_budget": monthly_budget,
            "months": months,
            "total_interest": total_interest,
            "total_paid": total_paid,
            "total_debt": total_debt,
        }
        self._write_results("\n".join(summary))
        messagebox.showinfo("Calculation Complete", "Payoff calculation finished. Export the results if desired.")

    def _save_debt_list(self):
        write_debt_entries_to_file(self.debts, DEBT_LIST_PATH)

    def _write_results(self, text):
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.config(state="disabled")

    def export_results(self):
        if not self.simulation_results or not self.sorted_debts:
            messagebox.showwarning("No Results", "Calculate the payoff results before exporting.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Save payoff results",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="Debt_Payoff_Results.csv",
        )
        if not filepath:
            return

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Debt Payoff Results"])
                writer.writerow(["Method", self.simulation_results["method"].capitalize()])
                writer.writerow(["Monthly Budget", f"${self.simulation_results['monthly_budget']:.2f}"])
                writer.writerow(["Months to Payoff", self.simulation_results["months"]])
                writer.writerow(["Total Interest Paid", f"${self.simulation_results['total_interest']:.2f}"])
                writer.writerow(["Total Paid", f"${self.simulation_results['total_paid']:.2f}"])
                writer.writerow(["Total Debt", f"${self.simulation_results['total_debt']:.2f}"])
                writer.writerow([])
                writer.writerow(["Debt Name", "Balance", "Interest Rate", "Minimum Payment"])
                for debt in self.sorted_debts:
                    writer.writerow([
                        debt.name,
                        f"${debt.balance:,.2f}",
                        f"{debt.interest_rate:.2%}",
                        f"${debt.minimum_payment:,.2f}",
                    ])
            messagebox.showinfo("Export Complete", f"Results exported to {filepath}")
        except Exception as exc:
            messagebox.showerror("Export Failed", f"Unable to write CSV: {exc}")


def run_app():
    root = tk.Tk()
    app = DebtPlannerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
