import streamlit as st
from utils.sheets_client import SheetsClient

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
        venta = sheets.get_sale_by_id(venta_id)

        if not venta:
            st.error("❌ No existe una venta con ese ID")
            return

        st.success("✔ Venta encontrada")

        # Datos generales (primer registro)
        info = venta[0]

        st.markdown("### 🧾 Información General")
        st.write(f"**ID:** {info['venta_id']}")
        st.write(f"**Fecha:** {info['fecha']}")
        st.write(f"**Cliente:** {info['cliente']}")
        st.write(f"**Observaciones:** {info['observaciones'] or '—'}")

        # Mostrar tabla con todos los ítems
        st.markdown("### 🛒 Detalle de Venta")

        total_general = 0
        for row in venta:
            total_general += float(row["precio total"])

        # Mostrar productos en tabla visual
        import pandas as pd

        df = pd.DataFrame(venta)
        df = df[[
            "producto",
            "cantidad",
            "precio unitario",
            "extra",
            "precio total"
        ]]

        st.table(df)

        st.markdown("---")
        st.write(f"### 💵 Total General: **S/. {total_general:.2f}**")
