CS 110 Group Project
# Debt Payment Calculator and Planner

A simple Python debt payment planner that uses a Tkinter GUI to build debt entries, choose a payment strategy, and calculate payoff timelines.

## What it does

- lets the user enter debt accounts with:
  - name
  - balance
  - interest rate
  - minimum payment
- supports both payoff strategies:
  - **Snowball** (smallest balance first)
  - **Avalanche** (highest interest rate first)
- calculates:
  - months to pay off all debt
  - total interest paid
  - total amount paid
- exports results to CSV

## Files

- `GUI.py` — Tkinter user interface for building debts, choosing strategy, and running calculations
- `Debt_Payment_Calculator_Plan/Debt_entry.py` — debt entry model and file helpers
- `Debt_Payment_Calculator_Plan/Snowball_Method.py` — load and sort debts by smallest balance
- `Debt_Payment_Calculator_Plan/Avalanche_Method.py` — load and sort debts by highest interest rate
- `Debt_Payment_Calculator_Plan/Debt_Calculator.py` — interactive console calculator and CSV export logic
- `Debt_Payment_Calculator_Plan/Debt_list.txt` — stored debt entries used by the planner

## Run locally

From the project root:

```bash
python GUI.py
```

Then use the GUI to add debts, choose Snowball or Avalanche, enter your monthly budget, and calculate your payoff plan.


## Notes

- The GUI writes debt entries to `Debt_Payment_Calculator_Plan/Debt_list.txt`
- Exported results can be saved as CSV from the GUI
