from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
#

def generate_pdf_report(report_dict: dict) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x, y = 40, height - 40
    c.setFont('Helvetica-Bold', 16)
    c.drawString(x, y, 'CyberCopAI - Incident Report')
    y -= 30
    c.setFont('Helvetica', 11)
    for k, v in report_dict.items():
        if isinstance(v, list):
            v = ', '.join(map(str, v))
        line = f"{k}: {v}"
        c.drawString(x, y, line[:120])
        y -= 16
        if y < 80:
            c.showPage()
            y = height - 40
    c.save()
    buffer.seek(0)
    return buffer.read()