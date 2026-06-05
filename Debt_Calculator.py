import os
import sys
import csv
from datetime import datetime

try:
    from Debt_Payment_Calculator_Plan.Snowball_Method import load_and_sort_debts as load_snowball
    from Debt_Payment_Calculator_Plan.Avalanche_Method import load_and_sort_debts as load_avalanche
    from Debt_Payment_Calculator_Plan.Debt_entry import create_debt_entries_from_input, write_debt_entries_to_file
except ModuleNotFoundError:
    sys.path.insert(0, os.path.dirname(__file__))
    from Snowball_Method import load_and_sort_debts as load_snowball
    from Avalanche_Method import load_and_sort_debts as load_avalanche
    from Debt_entry import create_debt_entries_from_input, write_debt_entries_to_file


def get_user_method():
    """Prompt user to choose snowball or avalanche method."""
    while True:
        print("\nChoose a debt payment strategy:")
        print("1. Snowball (pay off smallest balance first)")
        print("2. Avalanche (pay off highest interest rate first)")
        choice = input("Enter 1 or 2: ").strip()
        if choice in ["1", "2"]:
            return "snowball" if choice == "1" else "avalanche"
        print("Invalid choice. Please enter 1 or 2.")


def get_monthly_budget():
    """Prompt user for their monthly debt payment budget."""
    while True:
        try:
            budget = float(input("Enter your monthly debt payment budget ($): ").strip())
            if budget <= 0:
                print("Budget must be greater than 0.")
                continue
            return budget
        except ValueError:
            print("Please enter a valid number.")


def simulate_debt_payoff(debts, monthly_budget):
    """Simulate debt payoff and return (months, total_interest_paid).
    
    debts: list of DebtEntry objects (already sorted by chosen method)
    monthly_budget: total amount available each month for debt payment
    """
    # Make copies so we don't modify original objects
    working_debts = []
    for d in debts:
        from copy import copy
        working_debts.append(copy(d))
    
    months = 0
    total_interest_paid = 0.0
    
    # Simulate month by month until all debts are paid
    while any(debt.balance > 0 for debt in working_debts):
        months += 1
        
        # Apply monthly interest to each debt
        for debt in working_debts:
            if debt.balance > 0:
                monthly_interest = debt.balance * (debt.interest_rate / 12)
                debt.balance += monthly_interest
                total_interest_paid += monthly_interest
        
        # Determine which debts to prioritize
        # For both methods, first pay minimum payments on all debts
        remaining_budget = monthly_budget
        
        # Pay minimums on all debts
        for debt in working_debts:
            if debt.balance > 0 and remaining_budget > 0:
                payment = min(debt.minimum_payment, debt.balance, remaining_budget)
                debt.balance -= payment
                remaining_budget -= payment
        
        # Find the target debt (smallest balance for snowball, highest rate for avalanche)
        # This is already determined by the order of the sorted list
        if remaining_budget > 0:
            for debt in working_debts:
                if debt.balance > 0:
                    payment = min(debt.balance, remaining_budget)
                    debt.balance -= payment
                    remaining_budget -= payment
                    break
        
        # Safety check to prevent infinite loop
        if months > 600:
            print("Warning: Simulation exceeded 600 months. Stopping.")
            break
    
    return months, total_interest_paid


def export_to_csv(debts, method, months, total_interest, monthly_budget):
    """Ask user if they want to export debt entries and payoff results to CSV."""
    while True:
        response = input("\nDo you want to export your debt entries and payoff results to a CSV file? (yes/no): ").strip().lower()
        if response in ["yes", "y"]:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Debt_Payoff_Results_{timestamp}.csv"
            filepath = os.path.join(os.path.dirname(__file__), filename)
            
            try:
                with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write summary section
                    writer.writerow(["DEBT PAYOFF SUMMARY"])
                    writer.writerow(["Export Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                    writer.writerow(["Method", method.capitalize()])
                    writer.writerow(["Monthly Budget", f"${monthly_budget:.2f}"])
                    writer.writerow([])
                    
                    # Write payoff results
                    writer.writerow(["PAYOFF RESULTS"])
                    years = months // 12
                    remaining = months % 12
                    writer.writerow(["Total Months to Payoff", months])
                    writer.writerow(["Years and Months", f"{years}y {remaining}m"])
                    writer.writerow(["Total Interest Paid", f"${total_interest:.2f}"])
                    total_debt = sum(d.balance for d in debts)
                    total_paid = total_debt + total_interest
                    writer.writerow(["Total Amount Paid", f"${total_paid:.2f}"])
                    writer.writerow(["Original Total Debt", f"${total_debt:.2f}"])
                    writer.writerow([])
                    
                    # Write debt entries
                    writer.writerow(["DEBT ENTRIES"])
                    writer.writerow(["Name", "Balance", "Interest Rate", "Minimum Payment"])
                    for debt in debts:
                        writer.writerow([debt.name, f"${debt.balance:.2f}", f"{debt.interest_rate:.2%}", f"${debt.minimum_payment:.2f}"])
                
                print(f"\nResults exported successfully to: {filepath}")
                return filepath
            except Exception as e:
                print(f"Error writing to CSV: {e}")
                return None
        elif response in ["no", "n"]:
            print("Skipping CSV export.")
            return None
        else:
            print("Please enter 'yes' or 'no'.")


def main():
    print("=" * 60)
    print("DEBT PAYOFF CALCULATOR")
    print("=" * 60)
    
    # Build debt list interactively
    print("\nFirst, let's build your debt list.")
    debts = create_debt_entries_from_input()
    debt_file_path = os.path.join(os.path.dirname(__file__), "Debt_list.txt")
    write_debt_entries_to_file(debts, debt_file_path)
    print(f"Saved {len(debts)} debts to {debt_file_path}\n")
    
    # Get user inputs
    method = get_user_method()
    monthly_budget = get_monthly_budget()
    
    print(f"\nLoading debts using {method.capitalize()} method...")
    
    # Load and sort debts using chosen method
    if method == "snowball":
        debts = load_snowball()
    else:
        debts = load_avalanche()
    
    print(f"Loaded {len(debts)} debts.")
    print("\nDebt list:")
    for debt in debts:
        print(f"  {debt.name}: ${debt.balance:.2f} @ {debt.interest_rate:.2%}")
    
    # Calculate total debt
    total_debt = sum(debt.balance for debt in debts)
    print(f"\nTotal debt: ${total_debt:.2f}")
    print(f"Monthly budget: ${monthly_budget:.2f}")
    
    # Simulate payoff
    print("\nSimulating payoff...")
    months, total_interest = simulate_debt_payoff(debts, monthly_budget)
    
    years = months // 12
    remaining_months = months % 12
    total_paid = total_debt + total_interest
    
    print("\n" + "=" * 60)
    print("PAYOFF RESULTS")
    print("=" * 60)
    print(f"Method: {method.capitalize()}")
    print(f"Months to pay off: {months} ({years} years and {remaining_months} months)")
    print(f"Total interest paid: ${total_interest:.2f}")
    print(f"Total amount paid: ${total_paid:.2f}")
    print("=" * 60)
    
    # Offer to export results to CSV
    export_to_csv(debts, method, months, total_interest, monthly_budget)


if __name__ == "__main__":
    main()
