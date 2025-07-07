import os
import re
import fitz  # PyMuPDF
import imaplib
import email
import hashlib
from datetime import datetime
from email.header import decode_header
from dateutil import parser as date_parser

TMP_DIR = "./tmp/invoice_pdfs"
os.makedirs(TMP_DIR, exist_ok=True)

PLATFORM_FILTERS = {
    "Swiggy": 'FROM "Swiggy"',
    # Add more platforms here as needed
}

def log(msg):
    LOG_FILE = f"invoice_log_{datetime.now().date()}.log"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

def get_email_date(msg):
    try:
        raw_date = msg.get("Date")
        dt = date_parser.parse(raw_date)
        return dt.replace(tzinfo=None)
    except Exception as e:
        log(f"⚠️ Date parse issue, skipping email: {e}")
        return None

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

def fetch_invoices_from_all_pdfs(email_user, email_pass, user_id):
    log(f"\n📥 Connecting to Gmail for: {email_user}")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_user, email_pass)
        log("🔐 IMAP Login Successful")
    except Exception as e:
        log(f"❌ IMAP Login Failed: {e}")
        return {"invoices": []}

    MAX_PER_PLATFORM = 3
    total_fetched = 0
    final_invoices = []

    for platform, search_filter in PLATFORM_FILTERS.items():
        mail.select("inbox")
        status, messages = mail.search(None, search_filter)
        if status != "OK":
            log(f"⚠️ No emails found for {platform}")
            continue

        email_ids = messages[0].split()[::-1]
        pushed = 0
        log(f"🔍 Searching {platform}: Found {len(email_ids)} emails")

        for eid in email_ids:
            if pushed >= MAX_PER_PLATFORM:
                break

            _, msg_data = mail.fetch(eid, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            dt = get_email_date(msg)
            if not dt:
                continue

            for part in msg.walk():
                content_dispo = part.get("Content-Disposition", "")
                if part.get_content_type() == "application/pdf" and "attachment" in content_dispo:
                    pdf = part.get_payload(decode=True)
                    text, platform_extracted = extract_text_from_pdf(pdf)
                    if not text.strip() or not platform_extracted:
                        log("⚠️ Skipped PDF (no valid invoice info found)")
                        continue

                    amount = extract_amount(text)
                    if amount:
                        invoice = {
                            "user_id": user_id,
                            "platform": platform_extracted,
                            "amount": amount,
                            "date_fetched": dt.date().isoformat()
                        }

                        pushed += 1
                        total_fetched += 1
                        final_invoices.append(invoice)
                        log(f"✅ Added Invoice: ₹{amount} - {platform_extracted}")
                        break

    mail.logout()
    log(f"📦 Total Invoices Parsed: {total_fetched}")
    return {"invoices": final_invoices}

__all__ = ["fetch_invoices_from_all_pdfs"]
