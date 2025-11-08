# utils/data.py
import streamlit as st

PLATOS = {
    "Pollo": 21.00,
    "Chuleta": 25.00,
    "Churrasco": 28.00,
    "Tira de Cerdo": 31.00,
    "Filete de Pechuga": 26.00,
    "Porción de Molleja": 18.00,
    "Unidad de Chorizo": 9.00,
}

BEBIDAS = {
    "Cerveza": 8.00,
    "Jarra de Chicha": 15.00,
    "Gaseosa": 6.50,
    "Limonada": 15.00,
}

EXTRA_PAPAS = 4.50
EXTRA_TAPER = 1.50

def init_session_state():
    if "cart" not in st.session_state:
        st.session_state.cart = []
