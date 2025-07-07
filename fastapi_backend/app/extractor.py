import os
import re
import fitz  # PyMuPDF
import imaplib
import email
import requests
import hashlib
from datetime import datetime, timedelta
from email.header import decode_header
from dateutil import parser as date_parser



# ===== CONFIG =====
TMP_DIR = "./tmp/invoice_pdfs"
os.makedirs(TMP_DIR, exist_ok=True)

# 🧠 In-memory cache of invoice hashes per user
invoice_hash_cache = {}

# ===== LOGGING =====
def log(msg):
    LOG_FILE = f"invoice_log_{datetime.now().date()}.log"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

# ===== UTILS =====
def get_email_date(msg):
    try:
        raw_date = msg.get("Date")
        dt = date_parser.parse(raw_date)
        if dt.tzinfo is not None:
            dt = dt.astimezone(tz=None).replace(tzinfo=None)
        return dt
    except Exception as e:
        log(f"⚠️ Date parse issue, skipping email: {e}")
        return None

def generate_pdf_hash(pdf_bytes):
    return hashlib.sha256(pdf_bytes).hexdigest()

def extract_text_from_pdf(pdf_bytes):
    try:
        tmp_path = os.path.join(TMP_DIR, f"invoice_{datetime.now().timestamp()}.pdf")
        with open(tmp_path, "wb") as f:
            f.write(pdf_bytes)

        doc = fitz.open(tmp_path)
        if doc.is_encrypted:
            log(f"🔐 Skipped encrypted PDF: {os.path.basename(tmp_path)}")
            return "", None

        text = "".join([page.get_text() for page in doc])
        doc.close()
        os.remove(tmp_path)

        platform = get_platform_from_text(text)
        return text, platform
    except Exception as e:
        log(f"❌ PDF parse error: {e}")
        return "", None

def extract_amount(text):
    patterns = [
        r"₹\s?(\d[\d,]*\.?\d*)",
        r"Rs\.?\s?(\d[\d,]*\.?\d*)",
        r"INR\s?(\d[\d,]*\.?\d*)",
        r"Invoice Total\s+(\d+\.\d{2})",
        r"Total Amount\s+(\d+\.\d{2})"
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for amt in matches:
            try:
                val = float(amt.replace(",", ""))
                if val > 10:
                    return val
            except:
                continue
    return None

def get_platform_from_text(text):
    lowered = text.lower()
    if "swiggy" in lowered:
        return "Swiggy"
    elif "zomato" in lowered:
        return "Zomato"
    elif "zepto" in lowered:
        return "Zepto"
    elif "amazon" in lowered:
        return "Amazon"
    return None

# ===== MAIN FUNCTION =====
def fetch_invoices_from_all_pdfs(email_user, email_pass, user_id):
    log(f"\n📥 Connecting to Gmail for: {email_user}")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_user, email_pass)
        log("🔐 IMAP Login Successful")
    except Exception as e:
        log(f"❌ IMAP Login Failed: {e}")
        return

    status, _ = mail.select("inbox")
    if status != "OK":
        log("❌ Failed to select inbox.")
        return

    status, messages = mail.search(None, "ALL")
    if status != "OK":
        log("❌ Email search failed.")
        return

    email_ids = messages[0].split()[::-1]
    log(f"📨 Total Emails Found: {len(email_ids)}")

    now = datetime.utcnow()
    first_day_this_month = now.replace(day=1)
    first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)
    cutoff_start = first_day_last_month
    cutoff_end = now

    pushed = 0
    MAX = 10
    invoice_store[user_id] = []

    if user_id not in invoice_hash_cache:
        invoice_hash_cache[user_id] = set()

    for eid in email_ids:
        if pushed >= MAX:
            break

        _, msg_data = mail.fetch(eid, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        dt = get_email_date(msg)
        if not dt or not (cutoff_start <= dt <= cutoff_end):
            continue

        for part in msg.walk():
            content_dispo = part.get("Content-Disposition", "")
            if part.get_content_type() == "application/pdf" and "attachment" in content_dispo:
                pdf = part.get_payload(decode=True)
                pdf_hash = generate_pdf_hash(pdf)

                # 🧠 Skip if already seen
                if pdf_hash in invoice_hash_cache[user_id]:
                    continue

                text, platform = extract_text_from_pdf(pdf)
                if not text.strip() or not platform:
                    log("⚠️ Skipped PDF (no valid invoice info found)")
                    continue

                amount = extract_amount(text)
                if amount:
                    invoice = {
                        "user_id": user_id,
                        "platform": platform,
                        "amount": amount,
                        "date_fetched": dt.date().isoformat(),
                        "is_new": True
                    }
                    invoice_store[user_id].append(invoice)
                    invoice_hash_cache[user_id].add(pdf_hash)
                    pushed += 1
                    log(f"✅ Added Invoice: ₹{amount} - {platform}")

    mail.logout()
    log(f"📦 Total Valid Invoices Parsed: {pushed}")

# === EXPORT ===
__all__ = ["fetch_invoices_from_all_pdfs"]
