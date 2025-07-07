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
def fetch_invoices(req: FetchRequest):
    try:
        fetch_invoices_from_all_pdfs(req.email_user, req.email_pass, req.user_id)
        return {"status": "success"}
    except Exception as e:
        log(f"❌ Error in fetch endpoint: {e}")
        return {"status": "error", "message": str(e)}

# 📤 Get invoices for a user
@app.get("/invoices/{user_id}")
def get_invoices(user_id: int):
    return invoice_store.get(user_id, [])
