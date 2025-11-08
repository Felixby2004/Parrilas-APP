import streamlit as st
from views import carta, ventas, historial
from utils.data import init_session_state


st.set_page_config(
    page_title="El Establo",
    page_icon="🥩",
    initial_sidebar_state="expanded",
    layout="wide"
)


# Inicializa session_state necesario
init_session_state()


with st.sidebar:
    st.title("🔥 Parrilladas - El Establo")
    page = st.radio("Ir a:", ["Carta", "Ventas", "Historial"])
    st.markdown("---")
    st.caption("Operación: Google Sheets para historial")


if page == "Carta":
    carta.show()
elif page == "Ventas":
    ventas.show()
elif page == "Historial":
    historial.show()

