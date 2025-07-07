
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

## 🐳 Setup Instructions (Docker)

> Make sure Docker and Docker Compose are installed

```bash
# Step 1: Clone the repo
git clone https://github.com/farisfarsan/smart_finance_manager.git
cd smart_finance_manager

# Step 2: Create a .env file
cp .env.example .env
# (Update Gmail credentials inside)

# Step 3: Build and run containers
docker-compose up --build
```

- Django will run at: [http://localhost:8000](http://localhost:8000)
- FastAPI will run at: [http://localhost:8001](http://localhost:8001)

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

---

## 📜 License

MIT License. Feel free to fork, modify, and build your own financial agent!

---
