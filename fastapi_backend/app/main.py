from fastapi import FastAPI
from pydantic import BaseModel
from app.extractor import fetch_invoices_from_all_pdfs


from datetime import datetime

# 🔍 Logger utility
def log(msg):
    LOG_FILE = f"invoice_log_{datetime.now().date()}.log"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

# 🚀 FastAPI App
app = FastAPI()

# 📬 Input model for invoice fetch request
class FetchRequest(BaseModel):
    email_user: str
    email_pass: str
    user_id: int

# ✅ Health check endpoint
@app.get("/")
def root():
    return {"message": "✅ FastAPI Invoice Parser running"}

# 📥 Trigger invoice fetching
@app.post("/fetch-invoices/")
def fetch_invoices(payload: dict):
    email_user = payload.get("email_user")
    email_pass = payload.get("email_pass")
    user_id = payload.get("user_id")

    if not email_user or not email_pass:
        return {"error": "Missing credentials"}, 400

    result = fetch_invoices_from_all_pdfs(email_user, email_pass, user_id)

    if result and "invoices" in result:
        return result  # ✅ Return dictionary to Django
    else:
        return {"invoices": []}  # Ensure it never returns None
