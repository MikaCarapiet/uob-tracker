# UOB Transaction Tracker

Reads UOB Singapore transaction alert emails via Gmail, logs them to Google Sheets, and notifies via Telegram.

No IMAP. No app passwords. No local CSV. Uses `gog` CLI (already authenticated via OAuth).

---

## Flow

```
Gmail (UOB alert arrives)
        ↓
gog gmail messages search → fetch unread UOB emails
        ↓
parser.py → extract amount, type, merchant, date
        ↓
categorizer.py → keyword match → category or None
        ↓
gog sheets append → log to Google Sheet
        ↓
    [category?]
    /         \
  YES          NO
   ↓            ↓
Telegram      Telegram inline buttons
confirm       → you tap → category saved
```

---

## Prerequisites

- `gog` CLI authenticated with your Gmail account
  - Install: `brew install steipete/tap/gogcli`
  - Auth: `gog auth add you@gmail.com --services gmail,sheets`
- Python 3.10+

---

## Setup

### 1. Clone

```bash
git clone https://github.com/MikaCarapiet/uob-tracker.git
cd uob-tracker
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

| Variable | Description |
|---|---|
| `GOG_BIN` | Path to gog binary (default: `/home/node/.local/bin/gog`) |
| `GOG_ACCOUNT` | Your Gmail address |
| `GOOGLE_SHEET_ID` | Sheet ID from the URL |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (from @BotFather) |
| `TELEGRAM_CHAT_ID` | Your Telegram chat/user ID |
| `UOB_SENDER_EMAIL` | UOB sender (default: `PaymentAlert@uob.com.sg`) |
| `POLL_INTERVAL` | Seconds between checks (default: `60`) |

### 4. Enable UOB eAlerts

1. Log in to UOB Personal Internet Banking
2. Go to **My Alerts** → enable transaction alerts → set delivery to **email**

### 5. Run

```bash
python main.py
```

---

## Google Sheet

Columns: `Date | Type | Currency | Amount | Description | Category | Account | Logged At`

Sheet is created automatically — no manual setup needed.

---

## Auto-categories

Keyword matching in `categorizer.py` → `CATEGORIES` dict:

- Food & Drink, Transport, Groceries, Shopping, Entertainment
- Bills & Utilities, Health & Fitness, Travel, El Matador

Unknown merchants trigger a Telegram prompt with inline buttons.

---

## Notes

- `.env` and `transactions.csv` are gitignored — your data stays private
- No credentials in code, ever
