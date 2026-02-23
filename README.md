# UOB Transaction Tracker

Auto-logs UOB Singapore transaction alert emails to CSV and notifies via Telegram.

**Flow:**
1. UOB sends a transaction alert email to your Gmail
2. This script polls Gmail via IMAP every N seconds
3. Parses the email → extracts amount, merchant, type, date
4. Auto-categorizes based on merchant keywords
5. Logs to `transactions.csv`
6. If category is **known** → sends a Telegram confirmation
7. If category is **unknown** → sends a Telegram prompt with inline buttons to categorize manually

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/MikaCarapiet/uob-tracker.git
cd uob-tracker
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your values:

| Variable | Description |
|---|---|
| `GMAIL_ADDRESS` | Your Gmail address |
| `GMAIL_APP_PASSWORD` | Gmail App Password (not your main password) |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token (from @BotFather) |
| `TELEGRAM_CHAT_ID` | Your Telegram chat/user ID |
| `UOB_SENDER_EMAIL` | UOB sender (default: `PaymentAlert@uob.com.sg`) |
| `POLL_INTERVAL` | How often to check email in seconds (default: `60`) |
| `TRANSACTIONS_LOG` | CSV output path (default: `transactions.csv`) |

### 4. Enable Gmail IMAP + App Password

1. Gmail → Settings → See all settings → Forwarding and POP/IMAP → **Enable IMAP**
2. Google Account → Security → 2-Step Verification → **App Passwords**
3. Generate an app password for "Mail" and paste it as `GMAIL_APP_PASSWORD`

### 5. Enable UOB eAlerts

1. Log in to UOB Personal Internet Banking
2. Go to **My Alerts** → enable transaction alerts → set delivery to **email**

### 6. Run

```bash
python main.py
```

Or run as a background service:

```bash
nohup python main.py >> tracker.log 2>&1 &
```

---

## Output

`transactions.csv` columns:

| date | type | currency | amount | description | category | account_last4 | logged_at |
|---|---|---|---|---|---|---|---|

---

## Auto-categories

The categorizer matches merchant keywords to:
- Food & Drink
- Transport
- Groceries
- Shopping
- Entertainment
- Bills & Utilities
- Health & Fitness
- Travel
- El Matador

Add your own keywords in `categorizer.py` → `CATEGORIES` dict.

---

## Notes

- No credentials are ever stored in code — `.env` is gitignored
- `transactions.csv` is gitignored (your financial data stays local)
- The parser handles UOB SG email formats; may need tuning if UOB changes their template
