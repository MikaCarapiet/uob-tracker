"""
UOB Transaction Tracker
-----------------------
Polls Gmail for UOB transaction alert emails, parses them,
auto-categorizes where possible, logs to CSV, and notifies via Telegram.

If category is unknown → sends Telegram message with inline buttons to categorize manually.
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
    gmail_address     = get_env("GMAIL_ADDRESS")
    gmail_app_password = get_env("GMAIL_APP_PASSWORD")
    telegram_token    = get_env("TELEGRAM_BOT_TOKEN")
    telegram_chat_id  = get_env("TELEGRAM_CHAT_ID")
    uob_sender        = os.getenv("UOB_SENDER_EMAIL", "PaymentAlert@uob.com.sg")
    poll_interval     = int(os.getenv("POLL_INTERVAL", "60"))
    tx_log_path       = os.getenv("TRANSACTIONS_LOG", "transactions.csv")

    log.info("UOB Tracker started. Polling every %ds.", poll_interval)
    log.info("Watching for emails from: %s", uob_sender)

    while True:
        try:
            emails = list(fetch_unread_uob_emails(gmail_address, gmail_app_password, uob_sender))

            if not emails:
                log.debug("No new UOB emails.")
            else:
                log.info("Found %d new UOB email(s).", len(emails))

            for uid, subject, body in emails:
                log.info("Processing email UID %s | Subject: %s", uid, subject)

                tx = parse_uob_email(subject, body)
                if not tx:
                    log.warning("Could not parse email UID %s. Skipping.", uid)
                    continue

                category = auto_categorize(tx.description)
                tx.category = category

                log_transaction(tx, tx_log_path)
                log.info("Logged: %s %s %.2f | %s | Category: %s",
                         tx.tx_type, tx.currency, tx.amount, tx.description, tx.category)

                if category:
                    send_logged_notification(telegram_token, telegram_chat_id, tx)
                else:
                    send_categorization_prompt(telegram_token, telegram_chat_id, tx)

        except Exception as e:
            log.error("Error in polling loop: %s", e, exc_info=True)

        time.sleep(poll_interval)


if __name__ == "__main__":
    run()
