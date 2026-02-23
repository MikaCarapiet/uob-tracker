"""
Google Sheets logger via gog CLI.
Appends transactions to the FinanceBot Sheet > Transactions tab.

Columns: Date | Category | Subcategory | Description | Amount | Currency | Amount (PHP) | Account | Tags | Notes
"""

import json
import subprocess
from parser import Transaction

# FinanceBot Sheet ID
FINANCEBOT_SHEET_ID = "1Ba_JE_rgD5d8MGKFyFSOM76MlWy2yhOzKhbpjTe3wVM"

# Rough SGD → PHP rate (update as needed or leave blank)
SGD_TO_PHP = 56.0


def log_transaction(tx: Transaction, gog_bin: str, account: str, sheet_id: str = FINANCEBOT_SHEET_ID) -> None:
    """Append a transaction row to the FinanceBot Sheet Transactions tab."""

    # Debit = negative spend, Credit = positive income
    signed_amount = -abs(tx.amount) if tx.tx_type == "DEBIT" else abs(tx.amount)
    amount_php = round(signed_amount * SGD_TO_PHP, 2) if tx.currency == "SGD" else ""

    row = [[
        tx.date,                              # Date
        tx.category or "Uncategorized",       # Category
        "",                                   # Subcategory (left for manual fill)
        tx.description,                       # Description
        signed_amount,                        # Amount
        tx.currency,                          # Currency
        amount_php,                           # Amount (PHP)
        f"UOB ····{tx.account_last4}",        # Account
        "uob-auto",                           # Tags
        tx.tx_type,                           # Notes
    ]]

    result = subprocess.run(
        [gog_bin, "sheets", "append", sheet_id, "Transactions!A:J",
         "--values-json", json.dumps(row),
         "--insert", "INSERT_ROWS",
         "--input", "USER_ENTERED",
         "--account", account, "--no-input"],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"gog sheets append failed: {result.stderr}")
