"""
Gmail IMAP watcher.
Polls for unread UOB transaction alert emails and yields raw (subject, body) tuples.
Uses Gmail App Password — no OAuth needed.
"""

import imaplib
import email
import email.header
import os
from typing import Generator, Tuple


def _decode_header(raw) -> str:
    parts = email.header.decode_header(raw)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return "".join(decoded)


def _get_body(msg) -> str:
    """Extract plain text body from email."""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            disp = str(part.get("Content-Disposition") or "")
            if ct == "text/plain" and "attachment" not in disp:
                charset = part.get_content_charset() or "utf-8"
                return part.get_payload(decode=True).decode(charset, errors="replace")
        # Fallback to HTML if no plain text
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                charset = part.get_content_charset() or "utf-8"
                raw_html = part.get_payload(decode=True).decode(charset, errors="replace")
                # Strip tags crudely
                import re
                return re.sub(r"<[^>]+>", " ", raw_html)
    else:
        charset = msg.get_content_charset() or "utf-8"
        return msg.get_payload(decode=True).decode(charset, errors="replace")
    return ""


def fetch_unread_uob_emails(
    gmail_address: str,
    gmail_app_password: str,
    uob_sender: str,
) -> Generator[Tuple[str, str, str], None, None]:
    """
    Connect to Gmail via IMAP, find unread emails from UOB sender,
    yield (uid, subject, body), then mark them as read.
    """
    with imaplib.IMAP4_SSL("imap.gmail.com") as imap:
        imap.login(gmail_address, gmail_app_password)
        imap.select("INBOX")

        # Search for unread emails from UOB sender
        status, data = imap.search(
            None, f'(UNSEEN FROM "{uob_sender}")'
        )
        if status != "OK":
            return

        uids = data[0].split()
        for uid in uids:
            status, msg_data = imap.fetch(uid, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            subject = _decode_header(msg.get("Subject", ""))
            body = _get_body(msg)

            yield uid.decode(), subject, body

            # Mark as read
            imap.store(uid, "+FLAGS", "\\Seen")
