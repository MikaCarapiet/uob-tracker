"""
CSV transaction logger.
Appends transactions to a local CSV file.
"""

import csv
import os
from datetime import datetime
from parser import Transaction


FIELDNAMES = ["date", "type", "currency", "amount", "description", "category", "account_last4", "logged_at"]


def log_transaction(tx: Transaction, filepath: str) -> None:
    """Append a transaction to the CSV log."""
    file_exists = os.path.isfile(filepath)

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "date": tx.date,
            "type": tx.tx_type,
            "currency": tx.currency,
            "amount": tx.amount,
            "description": tx.description,
            "category": tx.category or "Uncategorized",
            "account_last4": tx.account_last4,
            "logged_at": datetime.utcnow().isoformat(),
        })
