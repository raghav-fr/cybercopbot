from fastapi import FastAPI, Request
from app.whatsapp_integration import send_whatsapp_text
from app.firebase_config import db
from app.phishing_analyzer import analyze_link
from app.ai_module import extract_incident_details, generate_guidance
import re, json
#

app = FastAPI()

@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    body = await request.json()
    value = body["entry"][0]["changes"][0]["value"]
    if "messages" not in value:
        return {"status": "ignored"}

    msg = value["messages"][0]
    from_phone = msg["from"].split("@")[0]
    text = msg.get("text", {}).get("body", "").lower()

    # retrieve state
    user_ref = db.collection("users").document(from_phone)
    user_data = user_ref.get().to_dict() or {"state": "main_menu"}

    state = user_data.get("state", "main_menu")

    # ---- MAIN MENU ----
    if text in ["help", "hi", "hello", "menu", "start"] and state == "main_menu":
        menu = (
            "👮‍♂️ *Welcome to CyberCopAI*\n"
            "How can I help you today?\n\n"
            "1️⃣ Report a Cyber Crime\n"
            "2️⃣ Phishing Link / Number Analysis\n"
            "3️⃣ Cyber Safety Education\n"
            "4️⃣ Legal Awareness\n"
            "5️⃣ Step-by-Step Guidance for an Incident\n\n"
            "Please reply with a number or name."
        )
        await send_whatsapp_text(from_phone, menu)
        user_ref.set({"state": "main_menu"}, merge=True)
        return {"ok": True}

    # ---- MENU CHOICES ----
    if state == "main_menu":
        if "1" in text or "report" in text:
            await send_whatsapp_text(from_phone, "Please briefly describe the incident 📝")
            user_ref.set({"state": "reporting"}, merge=True)
            return {"ok": True}

        elif "2" in text or "phishing" in text:
            await send_whatsapp_text(from_phone, "Please send the suspicious *link* or *number* to analyze 🔍")
            user_ref.set({"state": "awaiting_phishing_link"}, merge=True)
            return {"ok": True}

        elif "3" in text or "education" in text:
            await send_whatsapp_text(from_phone, "📚 *Cyber Safety Tip:* Avoid sharing OTPs, bank details or personal info online. Would you like more lessons? (yes/no)")
            user_ref.set({"state": "education"}, merge=True)
            return {"ok": True}

        elif "4" in text or "legal" in text:
            await send_whatsapp_text(from_phone, "⚖️ You can file a complaint at https://cybercrime.gov.in or nearest police station. Want legal steps for a specific fraud? (yes/no)")
            user_ref.set({"state": "legal_awareness"}, merge=True)
            return {"ok": True}

        elif "5" in text or "guidance" in text:
            await send_whatsapp_text(from_phone, "Which type of incident do you need guidance for? (e.g., phishing, UPI fraud, sextortion)")
            user_ref.set({"state": "awaiting_guidance_topic"}, merge=True)
            return {"ok": True}

    # ---- REPORTING ----
    if state == "reporting":
        # Use LLM to extract fields
        extracted = extract_incident_details(text)
        missing_fields = [f for f in ["amount_lost", "bank_name", "date_time", "website_or_mail", "summary"]
                          if not extracted.get(f)]
        # Save extracted
        db.collection("complaints").add({"phone": from_phone, "description": text, "extracted_data": extracted})
        if missing_fields:
            next_field = missing_fields[0]
            await send_whatsapp_text(from_phone, f"Please provide the {next_field.replace('_', ' ')}:")
            user_ref.set({"state": "collecting_fields", "awaiting_field": next_field}, merge=True)
        else:
            await send_whatsapp_text(from_phone, "✅ Report collected successfully! Submitting to portal...")
            user_ref.set({"state": "main_menu"}, merge=True)
        return {"ok": True}

    # ---- COLLECTING ADDITIONAL FIELDS ----
    if state == "collecting_fields":
        awaiting_field = user_data.get("awaiting_field")

        # ✅ Fetch latest complaint
        complaint_docs = (
            db.collection("complaints")
            .where("phone", "==", from_phone)
            .order_by("timestamp")
            .limit_to_last(1)
            .get()
        )

        if not complaint_docs:
            await send_whatsapp_text(
                from_phone,
                "⚠️ No recent report found. Please start a new one by typing 'report'.",
            )
            user_ref.set({"state": "main_menu"}, merge=True)
            return {"ok": True}

        doc = complaint_docs[0]
        data = doc.to_dict()
        extracted = data.get("extracted_data", {})

        # ✅ Save current field
        extracted[awaiting_field] = text
        db.collection("complaints").document(doc.id).update(
            {"extracted_data": extracted}
        )

        # ✅ Determine remaining missing fields
        required_fields = ["amount_lost", "bank_name", "date_time", "website_or_mail", "summary"]
        missing_fields = [f for f in required_fields if not extracted.get(f)]

        if missing_fields:
            # Ask for the next one
            next_field = missing_fields[0]
            await send_whatsapp_text(
                from_phone, f"✅ Noted {awaiting_field.replace('_',' ')}.\nNow please provide the {next_field.replace('_',' ')}:"
            )
            user_ref.set(
                {"state": "collecting_fields", "awaiting_field": next_field},
                merge=True,
            )
        else:
            # ✅ All done
            await send_whatsapp_text(
                from_phone,
                "✅ All required details received!\nSubmitting your report to the Cyber Portal...",
            )
            user_ref.set({"state": "main_menu"}, merge=True)
            await send_whatsapp_text(
                from_phone,
                "🎯 Your report has been successfully recorded.\nWould you like to return to the main menu? (yes/no)",
            )

        return {"ok": True}


    # ---- PHISHING LINK ANALYSIS ----
    if state == "awaiting_phishing_link":
        result = analyze_link(text)
        await send_whatsapp_text(from_phone, result)
        user_ref.set({"state": "main_menu"}, merge=True)
        return {"ok": True}

    # ---- STEP-BY-STEP GUIDANCE ----
    if state == "awaiting_guidance_topic":
        response = generate_guidance(text)
        await send_whatsapp_text(from_phone, response)
        user_ref.set({"state": "main_menu"}, merge=True)
        return {"ok": True}

    return {"status": "ok"}
