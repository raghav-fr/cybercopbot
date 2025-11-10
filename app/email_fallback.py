import os
from email.message import EmailMessage
import smtplib

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))  # 465 for SSL

def send_report_email(to_email: str, subject: str, body_text: str, pdf_bytes: bytes, filename="report.pdf"):
    if not SMTP_USER or not SMTP_PASS:
        raise RuntimeError("SMTP credentials not set in env")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg.set_content(body_text)
    msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename=filename)

    # Use SSL
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)
    return {"ok": True, "msg": "sent"}
