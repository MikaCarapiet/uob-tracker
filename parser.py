"""
UOB email transaction parser.
Handles UOB Singapore transaction alert email formats.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Transaction:
    amount: float
    currency: str
    tx_type: str          # DEBIT or CREDIT
    description: str
    account_last4: str
    date: Optional[str]
    raw: str
    category: Optional[str] = field(default=None)


def parse_uob_email(subject: str, body: str) -> Optional[Transaction]:
    """
    Parse a UOB transaction alert email into a Transaction object.
    Returns None if the email doesn't match expected format.
    """
    body_clean = body.replace("\r\n", "\n").replace("\r", "\n")

    # Determine transaction type
    tx_type = None
    if re.search(r"\b(debit|debited|withdrawal|purchase|payment)\b", body_clean, re.IGNORECASE):
        tx_type = "DEBIT"
    elif re.search(r"\b(credit|credited|deposit|received)\b", body_clean, re.IGNORECASE):
        tx_type = "CREDIT"
    else:
        # Fallback: check subject
        if re.search(r"\bdebit\b", subject, re.IGNORECASE):
            tx_type = "DEBIT"
        elif re.search(r"\bcredit\b", subject, re.IGNORECASE):
            tx_type = "CREDIT"

    if tx_type is None:
        return None

    # Extract amount — e.g. SGD 45.50 or S$45.50 or SGD45.50
    amount_match = re.search(
        r"(SGD|S\$|USD|MYR|PHP)\s*([\d,]+\.\d{2})", body_clean, re.IGNORECASE
    )
    if not amount_match:
        return None

    currency = amount_match.group(1).upper().replace("S$", "SGD")
    amount = float(amount_match.group(2).replace(",", ""))

    # Extract account last 4 digits
    acct_match = re.search(r"[Aa]ccount\s*[Nn]o\.?\s*[:\-]?\s*[X*]{4,}\s*(\d{4})", body_clean)
    if not acct_match:
        # Try shorter pattern: XXXX-1234
        acct_match = re.search(r"[X*]{3,}-?(\d{3,4})", body_clean)
    account_last4 = acct_match.group(1) if acct_match else "????"

    # Extract description / merchant
    desc = _extract_description(body_clean)

    # Extract date
    date_match = re.search(
        r"(\d{1,2}\s+\w+\s+\d{4}|\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})",
        body_clean
    )
    date_str = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")

    return Transaction(
        amount=amount,
        currency=currency,
        tx_type=tx_type,
        description=desc,
        account_last4=account_last4,
        date=date_str,
        raw=body_clean[:500],
    )


def _extract_description(body: str) -> str:
    """
    Try multiple patterns to extract a meaningful merchant/description.
    """
    patterns = [
        r"(?:merchant|description|at|at merchant)[:\s]+([^\n\r]+)",
        r"(?:transaction\s+description|txn\s+desc)[:\s]+([^\n\r]+)",
        r"(?:reference|ref)[:\s]+([^\n\r]+)",
    ]
    for pattern in patterns:
        m = re.search(pattern, body, re.IGNORECASE)
        if m:
            return m.group(1).strip()

    # Last resort: grab first non-boilerplate line with uppercase words (likely merchant name)
    for line in body.split("\n"):
        line = line.strip()
        if len(line) > 5 and re.search(r"[A-Z]{2,}", line) and not re.search(
            r"(UOB|BANK|ACCOUNT|ALERT|NOTIFICATION|DEAR|CUSTOMER|SINGAPORE|LIMITED)", line
        ):
            return line

    return "Unknown"
