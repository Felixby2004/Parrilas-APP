# pages/carta.py
import streamlit as st

def show():
    st.header("📜 Carta")

    st.markdown(
        '<a href="https://www.canva.com/design/DAG56xiL4hw/P-wPRfxuGHtgF37Dxx0aEw/edit" target="_blank">Editar carta</a>',
        unsafe_allow_html=True
    )

    st.image("CARTA.png", width=500)
