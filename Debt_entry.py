import os

class DebtEntry:
    def __init__(self, name, balance, interest_rate, minimum_payment):
        self.name = name
        self.balance = balance
        self.interest_rate = interest_rate
        self.minimum_payment = minimum_payment


def _prompt_float(prompt, min_value=None):
    while True:
        try:
            raw = input(prompt).strip()
            value = float(raw)
            if min_value is not None and value < min_value:
                print(f"Enter a number >= {min_value}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number.")


def create_debt_entries_from_input():
    """Interactively prompt the user to build and return a list of DebtEntry objects.

    Enter an empty name to finish input.
    """
    entries = []
    while True:
        name = input("Name (leave empty to finish): ").strip()
        if not name:
            break
        balance = _prompt_float("Balance: ", min_value=0.0)
        interest = _prompt_float("Interest rate (as percent or decimal, e.g. 5 or 0.05): ")
        if interest > 1:
            interest = interest / 100.0
        minimum = _prompt_float("Minimum payment: ", min_value=0.0)
        entries.append(DebtEntry(name, balance, interest, minimum))
    return entries


def create_debt_entries_from_iterable(data):
    """Create DebtEntry objects from an iterable of tuples/lists:
    (name, balance, interest_rate, minimum_payment).
    Useful for programmatic creation and testing.
    """
    entries = []
    for item in data:
        name, balance, interest, minimum = item
        if interest > 1:
            interest = interest / 100.0
        entries.append(DebtEntry(name, float(balance), float(interest), float(minimum)))
    return entries


def write_debt_entries_to_file(entries, path=None):
    """Write a list of DebtEntry objects to a text file as CSV (no header).

    Each line: name,balance,interest_rate,minimum_payment
    interest_rate is written as a decimal (e.g. 0.05 for 5%).
    If `path` is None, writes to Debt_list.txt next to this module.
    """
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "Debt_list.txt")
    with open(path, "w", encoding="utf-8") as f:
        for e in entries:
            line = f"{e.name},{e.balance},{e.interest_rate},{e.minimum_payment}\n"
            f.write(line)
    return path


if __name__ == "__main__":
    print("Build debt entries interactively.\n")
    debts = create_debt_entries_from_input()
    print("\nCreated entries:")
    for d in debts:
        print(d)
    save_path = os.path.join(os.path.dirname(__file__), "Debt_list.txt")
    write_debt_entries_to_file(debts, save_path)
    print(f"\nSaved {len(debts)} entries to: {save_path}")