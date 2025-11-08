# pages/ventas.py
import streamlit as st
from utils.data import PLATOS, BEBIDAS, EXTRA_PAPAS, EXTRA_TAPER, init_session_state
from utils.pdf_generator import generate_ticket_bytes
from utils.sheets_client import SheetsClient

# Inicializa session_state si no existe
init_session_state()

# --- INICIALIZAR OBSERVACIONES ---
if "observaciones_input" not in st.session_state:
    st.session_state.observaciones_input = ""

_sheets_client = None
def get_sheets():
    global _sheets_client
    if _sheets_client is None:
        _sheets_client = SheetsClient()
    return _sheets_client

def show():
    st.header("🛒 Ventas")

    # Nombre del cliente
    client_name = st.text_input("Nombre del Cliente", key="cliente_input")

    st.subheader("🍽️ Platos")

    # Selección de plato + extras
    plato_select = st.selectbox("Selecciona un plato", ["Seleccionar"] + list(PLATOS.keys()))
    papas = False
    taper = False

    if plato_select != "Seleccionar":
        papas = st.checkbox("Agregar Papas Fritas")
        taper = st.checkbox("Agregar Taper")

    cantidad_plato = st.number_input("Cantidad de platos", min_value=0, value=0, step=1)

    if st.button("Agregar Plato al Carrito"):
        if plato_select == "Seleccionar" or cantidad_plato <= 0:
            st.warning("Selecciona un plato y una cantidad válida.")
        else:
            extras = []
            extra_cost = 0

            if papas:
                extras.append("Papas fritas")
                extra_cost += EXTRA_PAPAS*cantidad_plato
            if taper:
                extras.append("Taper")
                extra_cost += EXTRA_TAPER*cantidad_plato

            # Nombre final del producto
            name_final = plato_select + (" + " + " + ".join(extras) if extras else "")

            # Precio unitario final incluyendo extras
            unit_price = round(PLATOS[plato_select], 2)

            subtotal = round(unit_price * cantidad_plato + extra_cost, 2)

            st.session_state.cart.append({
                "name": name_final,
                "qty": int(cantidad_plato),
                "unit_price": unit_price,
                "extra": round(extra_cost, 2),
                "subtotal": subtotal
            })

            st.success(f"Agregado al carrito ✅")

    st.subheader("🥤 Bebidas")

    # Selección de bebida
    bebida_select = st.selectbox("Selecciona una bebida", ["Seleccionar"] + list(BEBIDAS.keys()))
    cantidad_bebida = st.number_input("Cantidad de bebidas", min_value=0, value=0, step=1, key="qty_bebida")

    if st.button("Agregar Bebida al Carrito"):
        if bebida_select == "Seleccionar" or cantidad_bebida <= 0:
            st.warning("Selecciona una bebida y una cantidad válida.")
        else:
            price = round(BEBIDAS[bebida_select], 2)
            subtotal = round(price * cantidad_bebida, 2)

            st.session_state.cart.append({
                "name": bebida_select,
                "qty": int(cantidad_bebida),
                "unit_price": price,
                "extra": 0.00,
                "subtotal": subtotal
            })

            st.success(f"Agregado al carrito ✅")

    # --- OBSERVACIONES ---
    observaciones = st.text_area("Observaciones (opcional)", key="observaciones_input")

    # --- CARRITO ABAJO ---
    st.markdown("---")
    st.subheader("🛒 Carrito de Compra")

    if not st.session_state.cart:
        st.info("El carrito está vacío. Agrega productos para continuar.")
        return

    total_general = 0

    # Mostrar carrito
    for i, item in enumerate(list(st.session_state.cart)):
        row = st.columns([4, 1, 2, 2, 2, 1])
        row[0].write(item["name"])
        row[1].write(item["qty"])
        row[2].write(f"S/. {item['unit_price']:.2f}")
        row[3].write(f"S/. {item['extra']:.2f}")
        row[4].write(f"S/. {item['subtotal']:.2f}")

        if row[5].button("🗑️", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

        total_general += item["subtotal"]

    st.markdown("---")
    st.write(f"### 💵 Total General: S/. {total_general:.2f}")

    # Registrar venta
    if st.button("✅ Registrar Venta y Guardar"):
        if not client_name or client_name.strip() == "":
            st.warning("Ingresa el nombre del cliente antes de registrar la venta.")
        else:
            try:
                sheets = get_sheets()
                venta_id = sheets.append_sale(client_name, st.session_state.cart, observaciones)
            except Exception as e:
                st.error(f"❌ Error guardando en Google Sheets: {e}")
                return

            # Guardar PDF en session_state
            pdf_bytes = generate_ticket_bytes(client_name, st.session_state.cart, total_general)
            st.session_state.last_pdf = pdf_bytes
            st.session_state.last_venta_id = venta_id

            # limpiar carrito
            st.session_state.cart = []
            st.session_state.observaciones = ""
            st.success(f"✅ Venta registrada correctamente (ID: {venta_id})")

            st.rerun()

    # ---- Mostrar botón de PDF después del rerun ----
    if "last_pdf" in st.session_state:
        st.download_button(
            "📥 Descargar comprobante PDF",
            data=st.session_state.last_pdf,
            file_name=f"ticket_{st.session_state.last_venta_id}.pdf",
            mime="application/pdf"
        )

