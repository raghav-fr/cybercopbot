# app/portal_integration.py
import os
import json
import requests
from typing import Dict, Any, Optional

PORTAL_ENDPOINT = os.getenv("PORTAL_API_ENDPOINT")  # e.g. https://cyberportal.gov/api/complaints
PORTAL_API_KEY = os.getenv("PORTAL_API_KEY")        # if required

def map_to_portal_schema(internal_report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert your internal extracted_data -> portal format.
    Adjust keys as per the portal API spec. This is a conservative, likely mapping.
    """
    ex = internal_report.get("extracted_data", internal_report)
    mapped = {
        "complaintId": internal_report.get("complaint_id"),
        "complainantName": ex.get("victim_name") or ex.get("user_name"),
        "mobile": ex.get("phone") or internal_report.get("phone"),
        "incidentType": ex.get("category"),
        "incidentSubType": ex.get("subcategory"),
        "incidentDateTime": ex.get("date_time"),
        "incidentLocation": ex.get("location"),
        "amountLost": ex.get("amount_lost") or ex.get("amount"),
        "bankName": ex.get("bank_name"),
        "accountOrUpi": ex.get("account_no") or ex.get("upi_id"),
        "transactionId": ex.get("transaction_id"),
        "referenceNo": ex.get("reference_no"),
        "narrative": ex.get("summary") or ex.get("narrative") or ex.get("original_message"),
        "evidenceLinks": ex.get("evidence_urls", []),
        # extra metadata
        "submittedBySystem": "CyberCopAI",
        "createdAt": internal_report.get("created_at")
    }
    # Remove None values
    return {k: v for k, v in mapped.items() if v is not None}

def submit_to_portal(report_json: Dict[str, Any], pdf_bytes: Optional[bytes] = None) -> Dict[str, Any]:
    """
    Try portal API POST with JSON + file upload. Returns portal response dict.
    If PORTAL_ENDPOINT is not set, returns a message describing the mapping.
    """
    if not PORTAL_ENDPOINT:
        return {"ok": False, "reason": "No portal endpoint configured", "payload": report_json}

    headers = {"Accept": "application/json"}
    if PORTAL_API_KEY:
        headers["Authorization"] = f"Bearer {PORTAL_API_KEY}"

    # If portal accepts multipart/form-data with file
    files = {
        "data": ("report.json", json.dumps(report_json), "application/json")
    }
    if pdf_bytes:
        files["evidence_pdf"] = ("report.pdf", pdf_bytes, "application/pdf")

    try:
        resp = requests.post(PORTAL_ENDPOINT, headers=headers, files=files, timeout=30)
        try:
            return {"ok": True, "status_code": resp.status_code, "response": resp.json()}
        except Exception:
            return {"ok": True, "status_code": resp.status_code, "response_text": resp.text}
    except Exception as e:
        return {"ok": False, "error": str(e)}
