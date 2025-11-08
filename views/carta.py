# pages/carta.py
import streamlit as st
from utils.data import PLATOS, BEBIDAS

def show():
    st.header("📜 Carta")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Platos")
        for name, price in PLATOS.items():
            st.write(f"**{name}** — S/. {price:.2f}")
    with col2:
        st.subheader("Bebidas")
        for name, price in BEBIDAS.items():
            st.write(f"**{name}** — S/. {price:.2f}")
