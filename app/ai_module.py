import google.generativeai as genai
import os

# Configure API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize model
model = genai.GenerativeModel("gemini-2.5-flash")

def extract_incident_details(text: str):
    prompt = f"""
    Extract the following fields from the user's description of a cyber incident:
    - category
    - subcategory
    - date_time
    - amount_lost
    - bank_name
    - website_or_mail
    - summary

    Input: {text}
    Respond in JSON format only, like:
    {{
      "category": "",
      "subcategory": "",
      "date_time": "",
      "amount_lost": "",
      "bank_name": "",
      "website_or_mail": "",
      "summary": ""
    }}
    """
    try:
        response = model.generate_content(prompt)
        text_response = response.text.strip()
        print("Gemini raw output:", text_response)
        # Try parsing JSON safely
        import json
        start = text_response.find("{")
        end = text_response.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text_response[start:end])
        return {}
    except Exception as e:
        print("Gemini extraction error:", e)
        return {}

def generate_guidance(topic: str):
    prompt = f"""
    You are CyberCopAI, a digital cybersecurity assistant in India.
    Provide a concise, step-by-step guide for someone facing {topic}.
    Include legal, safety, and reporting advice.
    Keep tone professional, supportive, and easy to follow.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Gemini guidance error:", e)
        return "⚠️ Could not generate guidance at the moment. Please try again later."
