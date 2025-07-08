# 💼 Smart Finance Manager

A full-stack Python application to **fetch**, **parse**, and **visualize** invoice data from your Gmail inbox.  
Built using **Django** (frontend) + **FastAPI** (microservice), it provides a smart financial dashboard with PDF exports, smart insights, and trend visualization.

---

## 🔧 Tech Stack

| Layer       | Framework | Purpose                                    |
|-------------|-----------|--------------------------------------------|
| Frontend    | Django    | UI rendering, user auth, insights dashboard |
| Backend API | FastAPI   | Handles Gmail parsing, PDF invoice extraction |
| Database    | SQLite    | Local development storage (default)         |
| Docker      | Compose   | Containerized services for easy deployment  |

---

## 🚀 Features

- 🔐 **User Login** and session handling
- 📩 **Fetch invoices** using Gmail App Password
- 🧠 **Smart Insights** comparing month-to-month spend
- 📊 **7-Day Spending Trends** via Chart.js
- 📄 **Downloadable PDF Reports** (WeasyPrint)
- ⚙️ Dockerized setup for isolated development

---

## 📂 Project Structure

```
smart_finance_manager/
├── django_frontend/        # Django app (templates, views, URLs)
├── fastapi_backend/        # FastAPI app (Gmail IMAP logic, PDF parsing)
├── Dockerfile.django       # Docker config for Django
├── Dockerfile.fastapi      # Docker config for FastAPI
├── docker-compose.yml      # Brings both services together
├── .env                    # Gmail credentials (excluded via .gitignore)
├── requirements.txt        # Shared dependencies
└── README.md
```

---

## 🧠 How It Works (FastAPI Invoice Extractor Logic)

The FastAPI microservice fetches and parses invoice PDFs from your Gmail inbox using the following logic:

### 📤 `extractor.py` Flow:

1. **Connect to Gmail (IMAP):**
   - Logs in using **App Password**
   - Filters emails by platform (`Swiggy`, `Zomato`, etc.)

2. **Search + Download PDF Attachments:**
   - Only **PDFs** are considered (ignores inline content)
   - Limit of 3 emails per platform (for speed)

3. **Extract Text + Platform:**
   - Uses `PyMuPDF` (`fitz`) to extract text
   - Identifies sender (Swiggy, Zomato, etc.) from PDF content

4. **Parse Amount + Date:**
   - Uses regular expressions to extract total spend
   - Uses email headers to get accurate invoice date

5. **Return to Django:**
   - A list of cleaned invoice objects with:
     - `amount`, `platform`, `date_fetched`

---

## 🗃️ Log Files

Every fetch is logged to a file:

```bash
invoice_log_2025-07-07.log
```

Each log contains:
- Email parsing status
- Skipped encrypted PDFs
- Any parsing errors
- Successfully extracted invoice summaries

You can find these logs inside the `fastapi_backend` root directory.

---

## ⚡️ How to Speed Up Invoice Fetching

While current fetching is sequential and capped at 3 PDFs/platform for simplicity, you can **speed up parsing** with:

| Strategy                          | Benefit                            |
|----------------------------------|-------------------------------------|
| ✅ Async PDF parsing              | Parallelizes file extraction        |
| ✅ Background task queue (Celery) | Offloads parsing to workers         |
| ✅ Platform-specific filtering    | Avoids unnecessary inbox searches   |
| ✅ Hashing parsed emails          | Prevents re-processing duplicates   |
| ✅ OAuth2 Gmail API               | Faster, more reliable than IMAP     |

---

## 🧪 How to Test if Everything Works

### ✅ 1. Access the dashboard

Visit `http://localhost:8000` → login or access directly if sessionless

### ✅ 2. Enter Gmail + App Password

- Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
- Generate one for "Mail" → "FinanceManager"
- Paste in the UI and click **Fetch Invoices**

### ✅ 3. Visual Confirmation

- You’ll see invoices fetched under **Fetched Invoices**
- Chart will populate if spend data exists in last 7 days
- Smart Insight will show % increase/decrease vs previous month
- Click **Download PDF** to test PDF export

---

## 📎 .env File Format

```env
DJANGO_SECRET_KEY=your-django-secret
DEBUG=True

EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
```

> ⚠️ Never commit your real `.env` — it's gitignored!

---

## 🛠️ Troubleshooting

- 🟥 **Chart not loading?** Ensure there are invoices from the last 7 days.
- 🔐 **500 Error on PDF Download?** Ensure `WeasyPrint` and its system dependencies are installed via Docker (libpango, libgdk, etc.)
- 🧩 **DisallowedHost error?** Add `0.0.0.0` or `localhost` to `ALLOWED_HOSTS` in `settings.py`.

---

## 🌱 Future Enhancements

- OAuth2-based Gmail access (more secure)
- PostgreSQL support for production
- Spending category breakdown (Food, Travel, etc.)
- Budget alerts + notifications
- Redis-backed caching to reduce repeat parsing
- Celery workers for background invoice extraction

---


