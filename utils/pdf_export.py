# utils/pdf_export.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def generate_pdf(summary, filename="combined_ab_summary.pdf"):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40

    for line in summary.split('\n'):
        c.drawString(40, y, line)
        y -= 20

    c.save()
    buffer.seek(0)
    return buffer
