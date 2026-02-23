"""
Google Sheets logger via gog CLI.
Appends transactions to the UOB Transaction Tracker sheet.
"""

import json
import subprocess
from datetime import datetime, timezone
from parser import Transaction


def log_transaction(tx: Transaction, gog_bin: str, account: str, sheet_id: str) -> None:
    """Append a transaction row to the Google Sheet."""
    row = [[
        tx.date,
        tx.tx_type,
        tx.currency,
        tx.amount,
        tx.description,
        tx.category or "Uncategorized",
        tx.account_last4,
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    ]]

    result = subprocess.run(
        [gog_bin, "sheets", "append", sheet_id, "Sheet1!A:H",
         "--values-json", json.dumps(row),
         "--insert", "INSERT_ROWS",
         "--input", "USER_ENTERED",
         "--account", account, "--no-input"],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"gog sheets append failed: {result.stderr}")
