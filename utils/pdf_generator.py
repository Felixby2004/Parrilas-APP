# utils/pdf_generator.py
import io
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from datetime import datetime
from zoneinfo import ZoneInfo

BUSINESS_NAME = "Parrilladas - El Establo"

def generate_ticket_bytes(client_name, items, total, observaciones=""):
    # Ticket 80 mm width
    width_mm = 80
    line_height_mm = 6
    margin_mm = 6
    n_lines = 6 + len(items) + (1 if observaciones else 0)  # agregar línea si hay observaciones
    height_mm = margin_mm*2 + n_lines * line_height_mm

    width = width_mm * mm
    height = height_mm * mm

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width, height))
    c.setFont("Helvetica-Bold", 10)
    y = height - margin_mm * mm

    # Nombre del negocio
    c.drawCentredString(width / 2, y, BUSINESS_NAME)
    y -= 8

    # Cliente
    c.drawString(margin_mm * mm, y, f"Cliente: {client_name}")
    y -= 24

    # Observaciones (si existen)
    if observaciones.strip():
        c.drawString(margin_mm * mm, y, f"Observaciones: {observaciones}")
        y -= 12

    # Cabecera de items
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin_mm * mm, y, "PEDIDO")
    c.drawRightString(width - margin_mm * mm, y, "SUBTOTAL")
    y -= 10
    c.setFont("Helvetica", 9)

    # Items
    for it in items:
        line = f"{it['name']} x{it['qty']}"
        c.drawString(margin_mm * mm, y, line)
        c.drawRightString(width - margin_mm * mm, y, f"S/. {it['subtotal']:.2f}")
        y -= 10

    y -= 10
    # Total
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_mm * mm, y, "TOTAL")
    c.drawRightString(width - margin_mm * mm, y, f"S/. {total:.2f}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()
