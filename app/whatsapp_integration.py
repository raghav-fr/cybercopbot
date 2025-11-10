# app/whatsapp_integration.py
import os
import hmac
import hashlib
import httpx
import logging
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET")  # optional, for signature verification
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "my_verify_token")
GRAPH_BASE = "https://graph.facebook.com/v22.0"

logger = logging.getLogger("whatsapp_integration")
logging.basicConfig(level=logging.INFO)


def get_messages_endpoint():
    if not PHONE_NUMBER_ID:
        raise RuntimeError("WHATSAPP_PHONE_NUMBER_ID not configured in env")
    return f"{GRAPH_BASE}/{PHONE_NUMBER_ID}/messages"


def format_phone(phone: str) -> str:
    """
    Format phone to international digits only. Expect full number including country code (e.g. 919876543210)
    """
    if not phone:
        return phone
    digits = "".join([c for c in phone if c.isdigit()])
    return digits


async def send_whatsapp_text(to: str, message: str) -> Dict[str, Any]:
    """
    Send a simple text message.
    `to` should be full international number (no +), e.g. "919876543210".
    Returns the HTTP response dict.
    """
    url = get_messages_endpoint()
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": format_phone(to),
        "type": "text",
        "text": {"body": message}
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers=headers, json=payload, timeout=20.0)
        try:
            return {"status_code": r.status_code, "json": r.json()}
        except Exception:
            return {"status_code": r.status_code, "text": r.text}


async def send_whatsapp_template(to: str, template_name: str, language_code: str = "en_US", components: Optional[list] = None) -> Dict[str, Any]:
    """
    Send a registered template message.
    - template_name: the name of the approved template in your WhatsApp app
    - components: optional list of components per WhatsApp template API (example below)
    Example components:
    [
      {
        "type": "body",
        "parameters": [
          {"type": "text", "text": "John"},
          {"type": "text", "text": "Incident ID: ABC123"}
        ]
      }
    ]
    """
    url = get_messages_endpoint()
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": format_phone(to),
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code}
        }
    }
    if components:
        payload["template"]["components"] = components

    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers=headers, json=payload, timeout=20.0)
        try:
            return {"status_code": r.status_code, "json": r.json()}
        except Exception:
            return {"status_code": r.status_code, "text": r.text}


async def get_media_url(media_id: str) -> Optional[str]:
    """
    Step 1: GET /{media_id} to receive a temporary download URL (JSON with 'url' field)
    """
    if not WHATSAPP_TOKEN:
        raise RuntimeError("WHATSAPP_TOKEN not configured")

    url = f"{GRAPH_BASE}/{media_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers, timeout=20.0)
        if r.status_code != 200:
            logger.error("Failed to get media info: %s %s", r.status_code, r.text)
            return None
        j = r.json()
        return j.get("url")


async def download_media(media_id: str, save_path: Optional[str] = None) -> Optional[bytes]:
    """
    Download media file bytes given a media_id.
    - Use get_media_url() to get the temporary URL, then GET it with Authorization header.
    - If save_path provided, writes file and returns bytes.
    """
    file_url = await get_media_url(media_id)
    if not file_url:
        return None
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    async with httpx.AsyncClient() as client:
        r = await client.get(file_url, headers=headers, timeout=60.0)
        if r.status_code != 200:
            logger.error("Failed to download media content: %s %s", r.status_code, r.text)
            return None
        content = r.content
        if save_path:
            try:
                with open(save_path, "wb") as fh:
                    fh.write(content)
            except Exception as e:
                logger.exception("Could not write file: %s", e)
        return content


# ---------- Webhook helpers -------------


def verify_webhook_challenge(params: Dict[str, str]) -> Optional[str]:
    """
    For GET verification call from Facebook (when you set webhook URL in App dashboard).
    Facebook sends hub.mode, hub.verify_token, hub.challenge.
    Return challenge string when verify_token matches.
    """
    mode = params.get("hub.mode") or params.get("mode")
    token = params.get("hub.verify_token") or params.get("verify_token")
    challenge = params.get("hub.challenge") or params.get("challenge")
    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        return challenge
    return None


def verify_webhook_signature(raw_body: bytes, signature_header: Optional[str]) -> bool:
    """
    Optional: verify the X-Hub-Signature-256 header using your app secret.
    signature_header is the header value like: 'sha256=<hex>'
    """
    if not WHATSAPP_APP_SECRET:
        # if app secret not set, skip verification
        logger.info("WHATSAPP_APP_SECRET not configured; skipping signature verification")
        return True
    if not signature_header:
        logger.warning("Missing signature header")
        return False
    try:
        sig_prefix = "sha256="
        if not signature_header.startswith(sig_prefix):
            return False
        signature = signature_header[len(sig_prefix):]
        mac = hmac.new(WHATSAPP_APP_SECRET.encode("utf-8"), msg=raw_body, digestmod=hashlib.sha256)
        expected = mac.hexdigest()
        return hmac.compare_digest(expected, signature)
    except Exception as e:
        logger.exception("Error verifying signature: %s", e)
        return False
