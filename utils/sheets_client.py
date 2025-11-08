# utils/sheets_client.py
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json

# Cambia si tu hoja tiene otro nombre
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

        # si secrets devuelve string, parsear
        if isinstance(info, str):
            info = json.loads(info)

        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
        client = gspread.authorize(creds)
        # abre hoja
        sh = client.open(SHEET_NAME)
        try:
            self.sheet = sh.worksheet(TAB_NAME)
        except Exception:
            # crear worksheet si no existe
            sh.add_worksheet(title=TAB_NAME, rows="1000", cols="20")
            self.sheet = sh.worksheet(TAB_NAME)
            # escribir cabecera por si es nueva
            header = ["venta_id","fecha","cliente","producto","qty","unit_price","extras","total_item"]
            self.sheet.append_row(header)

    def append_sale(self, client_name, cart_items):
        venta_id = int(datetime.utcnow().timestamp())
        rows = []
        for it in cart_items:
            row = [
                venta_id,
                datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                client_name,
                it['name'],
                it['qty'],
                f"{it['unit_price']:.2f}",
                it.get('extras',''),
                f"{it['subtotal']:.2f}"
            ]
            rows.append(row)
        # append in batch
        self.sheet.append_rows(rows, value_input_option='USER_ENTERED')
        return venta_id

    def get_all_sales_df(self):
        try:
            data = self.sheet.get_all_values()
            if len(data) <= 1:
                return pd.DataFrame()
            df = pd.DataFrame(data[1:], columns=data[0])
            # convertir tipos
            for c in ['qty','unit_price','total_item']:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors='coerce')
            return df
        except Exception as e:
            st.error(f"Error leyendo Google Sheets: {e}")
            return pd.DataFrame()
