import os
import sys

try:
    from Debt_Payment_Calculator_Plan.Debt_entry import DebtEntry, write_debt_entries_to_file
except ModuleNotFoundError:
    sys.path.insert(0, os.path.dirname(__file__))
    from Debt_entry import DebtEntry, write_debt_entries_to_file


def read_debt_entries_from_file(path=None):
    """Read DebtEntry objects from Debt_list.txt."""
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "Debt_list.txt")
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) != 4:
                raise ValueError(f"Invalid line in debt list: {line}")
            name, balance, interest_rate, minimum_payment = parts
            entries.append(
                DebtEntry(
                    name.strip(),
                    float(balance),
                    float(interest_rate),
                    float(minimum_payment),
                )
            )
    return entries


def sort_debt_entries_by_interest(entries):
    """Return a new list sorted from largest interest rate to smallest."""
    return sorted(entries, key=lambda entry: entry.interest_rate, reverse=True)


def load_and_sort_debts(path=None):
    debts = read_debt_entries_from_file(path)
    sorted_debts = sort_debt_entries_by_interest(debts)
    write_debt_entries_to_file(sorted_debts, path)
    return sorted_debts


if __name__ == "__main__":
    sorted_debts = load_and_sort_debts()
    save_path = os.path.join(os.path.dirname(__file__), "Debt_list.txt")
    write_debt_entries_to_file(sorted_debts, save_path)
    print("Debts sorted by interest rate (largest to smallest):")
    for debt in sorted_debts:
        print(f"{debt.name}: ${debt.balance:.2f} | Interest: {debt.interest_rate:.2%} | Minimum: ${debt.minimum_payment:.2f}")
    print(f"\nSaved sorted debt list to: {save_path}")
