import streamlit as st
import json
from utils.sheets_client import SheetsClient
from utils.pdf_generator import generate_ticket_bytes
import base64

# Obtener cliente Sheets (singleton)
_sheets_client = None
def get_sheets():
    global _sheets_client
    if _sheets_client is None:
        _sheets_client = SheetsClient()
    return _sheets_client


def show():
    st.header("📜 Historial de Ventas")

    st.subheader("🔍 Buscar venta por ID")

    venta_id = st.text_input("Ingrese el ID de venta", key="hist_id")

    if st.button("Buscar"):
        sheets = get_sheets()

        # Normalizar ID
        venta_id_str = str(venta_id).strip()

        if not venta_id_str.isdigit():
            st.error("❌ El ID debe ser un número válido.")
            return

        venta = sheets.get_sale_by_id(venta_id_str)

        if not venta:
            st.error("❌ No existe una venta con ese ID")
            return

        st.success("✔ Venta encontrada")

        # ------------------------------------------------------------
        # Obtener datos necesarios desde la venta
        # ------------------------------------------------------------
        cliente = venta["cliente"]
        observaciones = venta.get("observaciones", "")

        try:
            cart = json.loads(venta["cart_json"])
        except:
            st.error("❌ Error al leer el carrito.")
            return

        # Calcular total
        total_general = sum(float(item["subtotal"]) for item in cart)

        # ------------------------------------------------------------
        # Generar PDF
        # ------------------------------------------------------------
        pdf_bytes = generate_ticket_bytes(
            cliente,
            cart,
            total_general,
            observaciones
        )

        # ------------------------------------------------------------
        # Mostrar PDF en pantalla
        # ------------------------------------------------------------
        st.markdown("### 🧾 Comprobante de Venta")

        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        pdf_display = f"""
        <iframe 
            src="data:application/pdf;base64,{base64_pdf}" 
            width="100%" 
            height="700px" 
            type="application/pdf">
        </iframe>
        """
        st.markdown(pdf_display, unsafe_allow_html=True)
