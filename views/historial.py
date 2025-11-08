# pages/historial.py
import streamlit as st
import pandas as pd
from utils.sheets_client import SheetsClient

def show():
    st.header("📊 Historial de Ventas")

    try:
        s = SheetsClient()
    except Exception as e:
        st.error(f"Error inicializando SheetsClient: {e}")
        return

    df = s.get_all_sales_df()

    if df is None or df.empty:
        st.info("No hay ventas registradas aún.")
        return

    # ==========================
    # NORMALIZAR COLUMNAS
    # ==========================

    # Renombrar columnas antiguas a nuevas para mostrar
    rename_map = {
        "qty": "cantidad",
        "unit_price": "precio unitario",
        "extras": "extra",
        "total_item": "precio total"
    }

    df.rename(columns=rename_map, inplace=True)

    # Asegurar que existan todas las columnas nuevas
    required_cols = ["venta_id", "fecha", "cliente", "producto",
                     "cantidad", "precio unitario", "extra", "precio total"]

    for col in required_cols:
        if col not in df.columns:
            df[col] = None  # Rellenar si no existe

    # Reordenar columnas para mostrar
    df = df[required_cols]

    # ==========================

    st.dataframe(df, use_container_width=True)

    # Exportar CSV
    if st.button("📥 Exportar CSV"):
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Descargar CSV", data=csv, file_name="historial_ventas.csv", mime="text/csv")

    # Detalle por venta_id
    if "venta_id" in df.columns:
        ids = df["venta_id"].dropna().unique().tolist()
        if ids:
            sel = st.selectbox("Seleccionar ID de venta para ver detalle", options=["Seleccionar"] + ids)
            if sel != "Seleccionar":
                detalle = df[df["venta_id"] == sel]
                st.subheader(f"🧾 Detalle de Venta ID: {sel}")
                st.table(detalle)
