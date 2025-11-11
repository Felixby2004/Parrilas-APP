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
    client_size = 12  # más grande
    text_size = 9     # subido para mejor lectura

    # Ajuste: más caracteres antes del salto para ampliar PEDIDO
    MAX_CHARS_DESC = 38  # antes 32 (aumenta el ancho)
    MAX_CHARS_OBS = 42

    def wrapped_lines(text, max_chars):
        return wrap(text, max_chars)

    # Altura calculada dinámicamente
    lines_count = 6
    for it in items:
        line = f"{it['qty']} {it['name']}"
        lines_count += len(wrapped_lines(line, MAX_CHARS_DESC))
    if observaciones.strip():
        lines_count += len(wrapped_lines("Obs: " + observaciones, MAX_CHARS_OBS))

    line_height_mm = 5.2
    height_mm = margin_mm*2 + lines_count * line_height_mm
    height = height_mm * mm

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width, height))

    y = height - margin_mm * mm

    # Cliente centrado y más grande
    c.setFont("Helvetica-Bold", client_size)
    c.drawCentredString(width / 2, y, f"{client_name}")
    y -= 20

    # Observaciones con wrap
    if observaciones.strip():
        c.setFont("Helvetica", text_size)
        wrapped_obs = wrapped_lines("Obs: " + observaciones, MAX_CHARS_OBS)
        for line in wrapped_obs:
            c.drawString(margin_mm * mm, y, line)
            y -= 11
        y -= 6

    # Encabezados
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(margin_mm * mm, y, "PEDIDO")

    # Ajuste: mover subtotal más hacia la derecha
    subtotal_x = width - (margin_mm * mm) - 4  # + espacio extra
    c.drawRightString(subtotal_x, y, "SUBTOTAL")
    y -= 14

    # Items con wrap
    c.setFont("Helvetica", text_size)
    for it in items:
        line = f"{it['qty']} {it['name']}"
        wrapped = wrapped_lines(line, MAX_CHARS_DESC)
        for idx, part in enumerate(wrapped):
            c.drawString(margin_mm * mm, y, part)

            if idx == 0:
                c.drawRightString(subtotal_x, y, f"S/. {it['subtotal']:.2f}")

            y -= 11
        y -= 5

    # Total
    y -= 10
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_mm * mm, y, "TOTAL")
    c.drawRightString(subtotal_x, y, f"S/. {total:.2f}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()
