# utils/sheets_client.py
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json

SHEET_NAME = "Historial Parrilladas El Establo"
TAB_NAME = "Sheet1"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

class SheetsClient:
    def __init__(self):
        info = st.secrets.get("gcp_service_account")
        if not info:
            raise Exception("No se encontró 'gcp_service_account' en Streamlit secrets. Pega el JSON de la cuenta de servicio allí.")

        if isinstance(info, str):
            info = json.loads(info)

        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
        client = gspread.authorize(creds)

        sh = client.open(SHEET_NAME)
        try:
            self.sheet = sh.worksheet(TAB_NAME)
        except Exception:
            sh.add_worksheet(title=TAB_NAME, rows="1000", cols="20")
            self.sheet = sh.worksheet(TAB_NAME)

    def _get_next_venta_id(self):
        """Obtiene el siguiente ID incremental leyendo la última fila existente."""
        data = self.sheet.get_all_values()
        if len(data) <= 1:
            return 1  # si no hay filas de ventas
        try:
            last_id = int(data[-1][0])  # primera columna
            return last_id + 1
        except:
            return 1

    def append_sale(self, client_name, cart_items, observaciones=""):
        venta_id = self._get_next_venta_id()
        rows = []

        for it in cart_items:
            row = [
                venta_id,  # venta_id
                datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),  # fecha
                client_name,  # cliente
                it['name'],  # producto (ya viene + extras)
                it['qty'],  # cantidad
                f"{it['unit_price']:.2f}",  # precio unitario
                f"{it.get('extra', 0):.2f}",  # extra (monto)
                f"{it['subtotal']:.2f}",  # precio total por item
                observaciones  # nueva columna
            ]
            rows.append(row)

        self.sheet.append_rows(rows, value_input_option='USER_ENTERED')
        return venta_id

    def get_all_sales_df(self):
        """Lee toda la hoja y convierte numéricos si las columnas existen."""
        try:
            data = self.sheet.get_all_values()
            if len(data) <= 1:
                return pd.DataFrame()

            df = pd.DataFrame(data[1:], columns=data[0])

            # intentamos convertir valores numéricos si están presentes
            numeric_cols = ["cantidad", "precio unitario", "extra", "precio total"]
            for c in numeric_cols:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors='coerce')

            return df
        except Exception as e:
            st.error(f"Error leyendo Google Sheets: {e}")
            return pd.DataFrame()
        
        
    def get_sale_by_id(self, venta_id):
        """Devuelve TODAS las filas que pertenecen a un venta_id."""
        try:
            data = self.sheet.get_all_records()

            # Filtrar filas con el mismo venta_id
            venta = [row for row in data if str(row["venta_id"]) == str(venta_id)]

            if not venta:
                return None

            return venta  # Lista con múltiples filas
        except Exception as e:
            st.error(f"Error buscando venta por ID: {e}")
            return None
