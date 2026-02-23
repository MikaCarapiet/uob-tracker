"""
Telegram notifier.
- Sends auto-categorized transaction confirmations.
- Sends categorization prompts with inline buttons when category is unknown.
"""

import os
import requests
from typing import Optional
from parser import Transaction

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"

CATEGORY_BUTTONS = [
    ["Food & Drink", "Transport", "Groceries"],
    ["Shopping", "Entertainment", "Bills & Utilities"],
    ["Health & Fitness", "Travel", "El Matador"],
    ["Other"],
]


def _post(token: str, method: str, payload: dict) -> dict:
    url = TELEGRAM_API.format(token=token, method=method)
    r = requests.post(url, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()


def send_logged_notification(token: str, chat_id: str, tx: Transaction) -> None:
    """Notify that a transaction was auto-categorized and logged."""
    emoji = "🔴" if tx.tx_type == "DEBIT" else "🟢"
    text = (
        f"{emoji} *Transaction Logged*\n"
        f"💰 {tx.currency} {tx.amount:,.2f}\n"
        f"📋 {tx.description}\n"
        f"🏷️ Category: *{tx.category}*\n"
        f"📅 {tx.date}\n"
        f"🏦 Acct: ····{tx.account_last4}"
    )
    _post(token, "sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    })


def send_categorization_prompt(token: str, chat_id: str, tx: Transaction) -> None:
    """Send a categorization request with inline keyboard buttons."""
    emoji = "🔴" if tx.tx_type == "DEBIT" else "🟢"
    text = (
        f"{emoji} *New Transaction — Categorize?*\n"
        f"💰 {tx.currency} {tx.amount:,.2f}\n"
        f"📋 {tx.description}\n"
        f"📅 {tx.date}\n"
        f"🏦 Acct: ····{tx.account_last4}\n\n"
        f"_What category is this?_"
    )

    # Build callback_data as "cat:<category>|<amount>|<description>"
    keyboard = []
    for row in CATEGORY_BUTTONS:
        btn_row = []
        for cat in row:
            callback = f"cat:{cat}|{tx.amount}|{tx.description[:30]}"
            btn_row.append({"text": cat, "callback_data": callback})
        keyboard.append(btn_row)

    _post(token, "sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": {"inline_keyboard": keyboard},
    })
