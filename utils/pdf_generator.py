# utils/pdf_generator.py
import io
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from textwrap import wrap

def generate_ticket_bytes(client_name, items, total, observaciones=""):
    width_mm = 90
    margin_mm = 6
    width = width_mm * mm

    # Font sizes
    client_size = 10
    text_size = 8

    # Convert items & obs to count lines for height calculation
    def wrapped_lines(text, max_chars=32):
        return wrap(text, max_chars)

    lines_count = 6  # base
    for it in items:
        line = f"{it['qty']} {it['name']}"
        lines_count += len(wrapped_lines(line))
    if observaciones.strip():
        lines_count += len(wrapped_lines("Observaciones: " + observaciones, 36))

    line_height_mm = 5
    height_mm = margin_mm*2 + lines_count * line_height_mm
    height = height_mm * mm

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width, height))

    y = height - margin_mm * mm

    # Client centered and bigger
    c.setFont("Helvetica-Bold", client_size)
    c.drawCentredString(width / 2, y, f"{client_name}")
    y -= 16

    # Observaciones con wrap
    if observaciones.strip():
        c.setFont("Helvetica", text_size)
        wrapped_obs = wrapped_lines("Observaciones: " + observaciones, 36)
        for line in wrapped_obs:
            c.drawString(margin_mm * mm, y, line)
            y -= 10
        y -= 4

    # Headers
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin_mm * mm, y, "PEDIDO")
    c.drawRightString(width - margin_mm * mm, y, "SUBTOTAL")
    y -= 12

    # Items con auto-wrap
    c.setFont("Helvetica", text_size)
    for it in items:
        line = f"{it['qty']} {it['name']}"
        wrapped = wrapped_lines(line)
        for idx, part in enumerate(wrapped):
            c.drawString(margin_mm * mm, y, part)
            # Print subtotal only on first line
            if idx == 0:
                c.drawRightString(width - margin_mm * mm, y, f"S/. {it['subtotal']:.2f}")
            y -= 10
        y -= 5

    # Total
    y -= 10
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_mm * mm, y, "TOTAL")
    c.drawRightString(width - margin_mm * mm, y, f"S/. {total:.2f}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()
