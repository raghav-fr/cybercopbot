import re
from datetime import datetime
from app.firebase_config import db, bucket

PHONE_RE = re.compile(r"\d{10,15}")


def is_phone(s: str):
    if not s:
        return False
    digits = re.sub(r"\D", "", s)
    return bool(PHONE_RE.fullmatch(digits))


def parse_money(s: str):
    if not s:
        return None
    import re
    s2 = re.sub(r"[^\d.]", "", s)
    try:
        return float(s2)
    except Exception:
        return None


def parse_datetime(s: str):
    if not s:
        return None
    for fmt in ("%d-%m-%Y %H:%M", "%d/%m/%Y %H:%M", "%d-%m-%Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    return None


# Firestore helpers

def save_complaint(doc_id: str, payload: dict):
    db.collection('complaints').document(doc_id).set(payload)


def update_complaint(doc_id: str, payload: dict):
    db.collection('complaints').document(doc_id).update(payload)


def get_complaint(doc_id: str):
    doc = db.collection('complaints').document(doc_id).get()
    return doc.to_dict() if doc.exists else None


def upload_bytes_to_storage(bytes_data: bytes, path: str):
    blob = bucket.blob(path)
    blob.upload_from_string(bytes_data)
    blob.make_public()
    return blob.public_url