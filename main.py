"""
UOB Transaction Tracker
-----------------------
Uses gog CLI to read Gmail + write to Google Sheets.
No IMAP, no app passwords, no local CSV.

Flow:
  gog gmail search → parse → categorize → gog sheets append → Telegram notify
"""

import os
import time
import logging
from dotenv import load_dotenv

from email_watcher import fetch_unread_uob_emails
from parser import parse_uob_email
from categorizer import auto_categorize
from logger import log_transaction
from notifier import send_logged_notification, send_categorization_prompt

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def get_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(f"Missing required env var: {key}")
    return val


def run():
    gog_bin          = os.getenv("GOG_BIN", "/home/node/.local/bin/gog")
    gog_account      = get_env("GOG_ACCOUNT")
    telegram_token   = get_env("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = get_env("TELEGRAM_CHAT_ID")
    uob_sender       = os.getenv("UOB_SENDER_EMAIL", "PaymentAlert@uob.com.sg")
    sheet_id         = get_env("GOOGLE_SHEET_ID")
    poll_interval    = int(os.getenv("POLL_INTERVAL", "60"))

    log.info("UOB Tracker started. Polling every %ds via gog.", poll_interval)

    while True:
        try:
            emails = list(fetch_unread_uob_emails(gog_bin, gog_account, uob_sender))

            if not emails:
                log.debug("No new UOB emails.")
            else:
                log.info("Found %d new UOB email(s).", len(emails))

            for msg_id, subject, body in emails:
                log.info("Processing message %s | %s", msg_id, subject)

                tx = parse_uob_email(subject, body)
                if not tx:
                    log.warning("Could not parse message %s. Skipping.", msg_id)
                    continue

                tx.category = auto_categorize(tx.description)

                log_transaction(tx, gog_bin, gog_account, sheet_id)
                log.info("Logged to Sheets: %s %s %.2f | %s | %s",
                         tx.tx_type, tx.currency, tx.amount,
                         tx.description, tx.category)

                if tx.category:
                    send_logged_notification(telegram_token, telegram_chat_id, tx)
                else:
                    send_categorization_prompt(telegram_token, telegram_chat_id, tx)

        except Exception as e:
            log.error("Error in polling loop: %s", e, exc_info=True)

        time.sleep(poll_interval)


if __name__ == "__main__":
    run()
