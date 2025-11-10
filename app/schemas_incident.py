INCIDENT_SCHEMA = {
    "IncidentDetails": [
        {"key": "category", "label": "Category of complaint", "type": "string", "auto_fill": True, "required": True},
        {"key": "subcategory", "label": "Subcategory", "type": "string", "auto_fill": True, "required": True},
        {"key": "lost_money", "label": "Have you lost money?", "type": "boolean", "auto_fill": True, "required": True},
        {"key": "amount_lost", "label": "Amount lost (INR)", "type": "float", "auto_fill": True, "required": False},
        {"key": "date_time", "label": "Date and time of incident", "type": "datetime", "auto_fill": True, "required": True},
        {"key": "delay_reporting", "label": "Delay in reporting (days/hours)", "type": "string", "auto_fill": False, "required": False},
        {"key": "location", "label": "Where incident occurred", "type": "string", "auto_fill": True, "required": False},
        {"key": "platform", "label": "ID / Website / Email / Platform details", "type": "string", "auto_fill": True, "required": False},
        {"key": "supporting_evidence", "label": "Supporting evidence (screenshots, attachments)", "type": "files", "auto_fill": False, "required": False},
        {"key": "summary", "label": "Summary of the incident", "type": "text", "auto_fill": True, "required": True}
    ],

    "AccountFraud": [
        {"key": "bank_name", "label": "Bank / Wallet / Payment Merchant", "type": "string", "auto_fill": True, "required": True},
        {"key": "account_no", "label": "Account number / UPI ID", "type": "string", "auto_fill": True, "required": True},
        {"key": "transaction_id", "label": "Transaction ID", "type": "string", "auto_fill": True, "required": False},
        {"key": "amount", "label": "Transaction amount", "type": "float", "auto_fill": True, "required": True},
        {"key": "transaction_date", "label": "Transaction date", "type": "datetime", "auto_fill": True, "required": True},
        {"key": "reference_no", "label": "Reference No.", "type": "string", "auto_fill": True, "required": False},
        {"key": "fraudster_account", "label": "Fraudster account details (if any)", "type": "string", "auto_fill": True, "required": False}
    ]
}