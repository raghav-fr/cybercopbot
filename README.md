# 🚨 CyberCopAI – Intelligent Cyber Crime Reporting & Awareness Bot

It is an AI-powered WhatsApp chatbot that helps citizens report cyber crimes, analyze phishing links, and receive cyber safety education, legal guidance, and step-by-step incident help.

---

## 🧠 Features

### 💬 WhatsApp Chatbot
- Users can interact through WhatsApp using natural language.
- Provides 5 main functionalities:
  1. **Report a Cyber Crime** – Automatically extracts incident details using Google Gemini.
  2. **Phishing Link/Number Analysis** – Detects risky or fraudulent URLs and numbers.
  3. **Cyber Safety Education** – Sends AI-generated tips and best practices.
  4. **Legal Awareness** – Provides legal rights and steps for cyber fraud victims.
  5. **Step-by-Step Guidance** – Generates tailored guidance for specific crime types (e.g., UPI fraud, phishing, sextortion).

### 🧬 Intelligent NLP Extraction
- Uses **Gemini 1.5 Flash API** to extract structured fields from user descriptions.
- Automatically identifies:
  - `category`
  - `subcategory`
  - `amount_lost`
  - `bank_name`
  - `date_time`
  - `website_or_mail`
  - `summary`

### 🕵️‍♀️ Report Workflow
- Dynamically asks for missing fields.
- Saves reports to **Firebase Firestore**.
- Can be easily extended to auto-submit data to **cybercrime.gov.in** API.

### 🔍 Phishing Analyzer
- Scans links or numbers for suspicious patterns.
- Detects shorteners, insecure HTTP links, and keyword-based scams.

---

## 🏗️ Project Structure

```
cybercopai-backend/
│
├── app/
│   ├── main.py                   # FastAPI main application
│   ├── ai_module.py              # Gemini integration for NLP & guidance
│   ├── phishing_analyzer.py      # Link/number analysis logic
│   ├── whatsapp_integration.py   # Meta WhatsApp Cloud API integration
│   ├── firebase_config.py        # Firestore configuration
│   ├── utils.py                  # Utility and helper functions
│   ├── schemas_incident.py       # Defines required reporting fields
│   └── requirements.txt          # Dependencies
│
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/cybercopai-backend.git
cd cybercopai-backend
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r app/requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the root directory:

```
GEMINI_API_KEY=your_gemini_api_key_here
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
VERIFY_TOKEN=my_verify_token
FIREBASE_CREDENTIALS=serviceAccountKey.json
```

---

## 🔥 Firebase Configuration

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a Firestore database.
3. Add a service account key:
   - Settings → Project Settings → Service Accounts → Generate New Key
   - Save it as `serviceAccountKey.json` in the `app/` folder.
4. Your `firebase_config.py` should look like:

```python
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("app/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
```

---

## 🔊 WhatsApp Cloud API Setup

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app → Select “Business” → Add **WhatsApp Product**
3. Go to **Getting Started** under WhatsApp
4. Copy:
   - **Temporary Access Token**
   - **Phone Number ID**
   - **WhatsApp Business Account ID**
5. Set Webhook:
   - Callback URL: `https://<your-ngrok-url>/webhook`
   - Verify Token: `my_verify_token`
   - Subscribe to `messages` and `message_status` events.
6. Use [ngrok](https://ngrok.com/) or `devtunnel` for local webhook testing.

```bash
ngrok http 8000
```

---

## 🚀 Running the Server

```bash
uvicorn app.main:app --reload --port 8000
```

---

## 🤪 Testing Locally

1. Open Meta → WhatsApp → “Send Message”
2. Type `help`
3. Select:
   - “1” → Cyber Crime Reporting
   - “2” → Phishing Analysis
   - etc.
4. Follow bot prompts on your linked WhatsApp number.

---

## 🧠 AI Modules

### `extract_incident_details(text)`
Uses Gemini 1.5 Flash to extract structured JSON fields from user text.

### `generate_guidance(topic)`
Generates detailed, step-by-step victim support guidance.

---

## 📦 Example Conversation

```
User: help
Bot: 👮‍♂️ Welcome to CyberCopAI...
User: 1
Bot: Please describe the incident 📝
User: I lost ₹5000 to a fake bank call yesterday
Bot: Please provide the bank name
User: SBI
Bot: Please provide the date and time
User: Yesterday morning
...
Bot: ✅ All details received! Submitting your report...
```

---

## 🧰 Tech Stack

| Component | Technology |
|------------|-------------|
| Backend | FastAPI |
| AI | Google Gemini 1.5 Flash |
| Database | Firebase Firestore |
| Messaging | WhatsApp Cloud API |
| Hosting (local) | ngrok / DevTunnel |

---

## 🛡️ Future Enhancements

- Integration with **Cyber Crime Portal API**.
- Live **status tracking** for complaints.
- Add **voice support** using Twilio + Speech-to-Text.
- Multi-language support (Odia, Hindi, English).

---

## 👨‍💻 Authors

- Khageswar Deheri  

---


