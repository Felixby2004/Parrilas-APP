# pages/historial.py
import streamlit as st
from utils.sheets_client import SheetsClient
import pandas as pd

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

    st.dataframe(df)

    if st.button("Exportar CSV"):
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar CSV", data=csv, file_name="historial_ventas.csv", mime="text/csv")

    # ver detalle por venta_id (si existe columna)
    if "venta_id" in df.columns:
        ids = df["venta_id"].unique().tolist()
        sel = st.selectbox("Seleccionar ID de venta para ver detalle", options=[None] + ids)
        if sel:
            detail = df[df["venta_id"] == sel]
            st.table(detail[["venta_id","fecha","cliente","producto","qty","unit_price","extras","total_item"]])
