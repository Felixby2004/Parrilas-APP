# pages/ventas.py
import streamlit as st
from utils.data import PLATOS, BEBIDAS, EXTRA_PAPAS, EXTRA_TAPER, init_session_state
from utils.pdf_generator import generate_ticket_bytes
from utils.sheets_client import SheetsClient
from datetime import datetime

# ensure session state initialised (in case pages accessed directly)
init_session_state()

_sheets_client = None
def get_sheets():
    global _sheets_client
    if _sheets_client is None:
        _sheets_client = SheetsClient()
    return _sheets_client

def show():
    st.header("🛒 Ventas")
    # Nombre del cliente primero
    client_name = st.text_input("Nombre del Cliente", key="cliente_input")

    left, right = st.columns([2, 1])

    with left:
        st.subheader("Platos")
        for plato, price in PLATOS.items():
            cols = st.columns([3,1,1,1])
            cols[0].write(f"**{plato}** — S/. {price:.2f}")
            papas = cols[1].checkbox(f"Añadir Papas Fritas", key=f"papas_{plato}")
            taper = cols[2].checkbox(f"Añadir Taper", key=f"taper_{plato}")
            qty = cols[3].number_input("Cantidad", min_value=0, value=0, key=f"qty_{plato}")

            if qty > 0:
                if st.button(f"Agregar {plato}", key=f"add_{plato}"):
                    extra_cost = 0
                    extras = []
                    if papas:
                        extra_cost += EXTRA_PAPAS
                        extras.append("Papas")
                    if taper:
                        extra_cost += EXTRA_TAPER
                        extras.append("Taper")

                    name_final = plato + ( " + " + " + ".join(extras) if extras else "" )
                    unit_price = round(price + extra_cost, 2)
                    subtotal = round(unit_price * int(qty), 2)

                    st.session_state.cart.append({
                        "name": name_final,
                        "base_name": plato,
                        "qty": int(qty),
                        "unit_price": unit_price,
                        "subtotal": subtotal,
                        "extras": ", ".join(extras) if extras else ""
                    })
                    st.success(f"{name_final} x{qty} agregado al carrito")

        st.subheader("Bebidas")
        for bebida, price in BEBIDAS.items():
            cols = st.columns([3,1])
            cols[0].write(f"**{bebida}** — S/. {price:.2f}")
            qty = cols[1].number_input("Cantidad", min_value=0, value=0, key=f"qty_b_{bebida}")
            if qty > 0:
                if st.button(f"Agregar {bebida}", key=f"add_b_{bebida}"):
                    st.session_state.cart.append({
                        "name": bebida,
                        "base_name": bebida,
                        "qty": int(qty),
                        "unit_price": round(price,2),
                        "subtotal": round(price * int(qty),2),
                        "extras": ""
                    })
                    st.success(f"{bebida} x{qty} agregado al carrito")

    with right:
        st.subheader("Carrito")
        if not st.session_state.cart:
            st.info("El carrito está vacío. Agrega productos desde la columna izquierda.")
            return

        total = 0
        # show items
        for i, item in enumerate(list(st.session_state.cart)):
            row = st.columns([4,1,2,2,1])
            row[0].write(item["name"])
            row[1].write(item["qty"])
            row[2].write(f"S/. {item['unit_price']:.2f}")
            row[3].write(f"S/. {item['subtotal']:.2f}")
            # botón rojo pequeño solo icono
            if row[4].button("🗑️", key=f"del_{i}"):
                st.session_state.cart.pop(i)
                st.experimental_rerun()
            total += item["subtotal"]

        st.markdown("---")
        st.write(f"**Total: S/. {total:.2f}**")

        if st.button("Registrar Venta y Guardar"):
            if not client_name or client_name.strip() == "":
                st.warning("Ingresa el nombre del cliente antes de registrar la venta.")
            else:
                # guardar en Google Sheets
                try:
                    sheets = get_sheets()
                    venta_id = sheets.append_sale(client_name, st.session_state.cart)
                except Exception as e:
                    st.error(f"Error guardando en Google Sheets: {e}")
                    return

                # generar PDF y ofrecer descarga
                pdf_bytes = generate_ticket_bytes(client_name, st.session_state.cart, total)
                st.download_button("📥 Descargar comprobante PDF", data=pdf_bytes,
                                   file_name=f"ticket_{venta_id}.pdf", mime="application/pdf")

                # limpiar carrito
                st.session_state.cart = []
                st.success(f"Venta registrada (ID: {venta_id})")
                st.experimental_rerun()
