import streamlit as st
import base64
import streamlit.components.v1 as components
from utils.sheets_client import SheetsClient
from utils.pdf_generator import generate_ticket_bytes

# Singleton Sheets
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

        if not venta_id.strip().isdigit():
            st.error("❌ El ID debe ser un número.")
            return

        venta = sheets.get_sale_by_id(venta_id)

        if not venta:
            st.error("❌ No existe una venta con ese ID.")
            return

        st.success("✔ Venta encontrada")

        # --------------------------------------------------------
        #   Extraer datos generales desde la primera fila
        # --------------------------------------------------------
        fila0 = venta[0]
        cliente = fila0["cliente"]
        observaciones = fila0.get("observaciones", "")
        fecha = fila0["fecha"]

        # --------------------------------------------------------
        #   Convertir filas → carrito para el PDF
        # --------------------------------------------------------
        cart = []
        total = 0

        for row in venta:
            try:
                item = {
                    "name": row["producto"],
                    "qty": int(row["cantidad"]),
                    "unit_price": float(row["precio unitario"]),
                    "extra": float(row["extra"]),
                    "subtotal": float(row["precio total"])
                }
            except:
                st.error("⚠ Error procesando una fila de la venta.")
                return

            cart.append(item)
            total += item["subtotal"]

        # --------------------------------------------------------
        #   Generar PDF
        # --------------------------------------------------------
        pdf_bytes = generate_ticket_bytes(
            cliente,
            cart,
            total,
            observaciones
        )

        # --------------------------------------------------------
        #   Mostrar PDF en pantalla
        # --------------------------------------------------------
        st.markdown("### 🧾 Comprobante de Venta")

        b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

        pdf_html = f"""
            <embed 
                src="data:application/pdf;base64,{b64_pdf}"
                type="application/pdf"
                width="100%"
                height="700px"
            />
        """

        components.html(pdf_html, height=700)

        # --------------------------------------------------------
        #   Botón de descarga
        # --------------------------------------------------------
        st.download_button(
            "📥 Descargar Comprobante",
            data=pdf_bytes,
            file_name=f"venta_{venta_id}.pdf",
            mime="application/pdf"
        )
