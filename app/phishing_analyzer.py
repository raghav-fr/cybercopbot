# app/phishing_analyzer.py
import re, requests

def analyze_link(user_input: str) -> str:
    # Basic detection
    urls = re.findall(r'https?://[^\s]+', user_input)
    if not urls:
        return "⚠️ Please send a valid link (starting with http or https)."

    url = urls[0]
    # Heuristic risk signals
    risk_flags = []
    if re.search(r'\d+\.\d+\.\d+\.\d+', url):  # IP-based URL
        risk_flags.append("Uses direct IP address")
    if any(ext in url for ext in ["bit.ly", "tinyurl", "goo.gl", "t.co"]):
        risk_flags.append("Shortened link (possible masking)")
    if not re.search(r'https://', url):
        risk_flags.append("Not using HTTPS")
    if re.search(r'(login|bank|verify|update|secure)\.', url):
        risk_flags.append("Suspicious keyword")

    if risk_flags:
        report = "⚠️ *Potentially risky link detected!*\n\n" + "\n".join(f"• {f}" for f in risk_flags)
    else:
        report = "✅ The link looks normal based on initial checks.\n\n(For deeper scan, this can be connected to VirusTotal API)."

    return report
