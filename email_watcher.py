"""
Gmail watcher via gog CLI.
Fetches unread UOB transaction emails without IMAP or app passwords.
Requires: gog authenticated with Gmail access.
"""

import json
import subprocess
from typing import Generator, Tuple


def fetch_unread_uob_emails(
    gog_bin: str,
    account: str,
    uob_sender: str,
) -> Generator[Tuple[str, str, str], None, None]:
    """
    Use gog CLI to search for unread UOB transaction emails.
    Yields (message_id, subject, body) for each match.
    """
    query = f"from:{uob_sender} is:unread"

    result = subprocess.run(
        [gog_bin, "gmail", "messages", "search", query,
         "--max", "20", "--account", account, "--json"],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"gog gmail search failed: {result.stderr}")

    data = json.loads(result.stdout)
    messages = data.get("results", data) if isinstance(data, dict) else data

    for msg in messages:
        msg_id = msg.get("id", "")
        subject = msg.get("subject", "")
        body = msg.get("body", msg.get("snippet", ""))

        if not body:
            continue

        yield msg_id, subject, body

        # Mark as read
        subprocess.run(
            [gog_bin, "gmail", "messages", "modify", msg_id,
             "--remove-labels", "UNREAD",
             "--account", account, "--no-input"],
            capture_output=True, text=True
        )
