import streamlit as st
from utils.data import PLATOS, BEBIDAS, EXTRA_PAPAS, EXTRA_TAPER, init_session_state
from utils.pdf_generator import generate_ticket_bytes
from utils.sheets_client import SheetsClient

# Inicializa session_state
init_session_state()

if "observaciones_input" not in st.session_state:
    st.session_state.observaciones_input = ""

_sheets_client = None
def get_sheets():
    global _sheets_client
    if _sheets_client is None:
        _sheets_client = SheetsClient()
    return _sheets_client


# ======================================================================
#                           PANTALLA PRINCIPAL
# ======================================================================

def show():
    st.header("🛒 Ventas")

    # --------------------------------------------------------
    #  👤 CLIENTE
    # --------------------------------------------------------
    client_name = st.text_input("Nombre del Cliente", key="cliente_input")

    st.subheader("🍽️ Platos")
    plato_select = st.selectbox(
        "Selecciona un plato",
        ["Seleccionar"] + list(PLATOS.keys()),
        index=0
    )
    papas = False
    taper = False

    if plato_select != "Seleccionar":
        col1, col2 = st.columns(2)
        with col1:
            papas = st.checkbox("Agregar Papas Fritas")
        with col2:
            taper = st.checkbox("Agregar Taper")

    cantidad_plato = st.number_input("Cantidad de platos", min_value=0, value=0, step=1)

    # --------------------------------------------------------
    #   ➕ AGREGAR PLATO
    # --------------------------------------------------------
    if st.button("Agregar Plato al Carrito"):
        if plato_select == "Seleccionar" or cantidad_plato <= 0:
            st.warning("Selecciona un plato y una cantidad válida.")
        else:
            extras = []
            extra_cost = 0

            if papas:
                extras.append("Papas fritas")
                extra_cost += EXTRA_PAPAS * cantidad_plato
            if taper:
                extras.append("Taper")
                extra_cost += EXTRA_TAPER * cantidad_plato

            name_final = plato_select + (" + " + " + ".join(extras) if extras else "")
            unit_price = round(PLATOS[plato_select], 2)
            subtotal = round(unit_price * cantidad_plato + extra_cost, 2)

            st.session_state.cart.append({
                "name": name_final,
                "qty": int(cantidad_plato),
                "unit_price": unit_price,
                "extra": round(extra_cost, 2),
                "subtotal": subtotal
            })

            st.success("Agregado al carrito ✅")

    st.markdown("---")

    # --------------------------------------------------------
    #  🥤 BEBIDAS
    # --------------------------------------------------------
    st.subheader("🥤 Bebidas")

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

            st.success("Agregado al carrito ✅")

    st.markdown("---")

    # --------------------------------------------------------
    #   ✏️ OBSERVACIONES
    # --------------------------------------------------------
    observaciones = st.text_area("Observaciones (opcional)", key="observaciones_input")

    st.markdown("---")
    st.subheader("🛒 Carrito de Compra")

    if not st.session_state.cart:
        st.info("El carrito está vacío. Agrega productos para continuar.")
        return

    # --------------------------------------------------------
    #  LISTADO DEL CARRITO
    # --------------------------------------------------------
    total_general = 0

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

    # --------------------------------------------------------
    #  📄 PDF
    # --------------------------------------------------------
    pdf_client = client_name if client_name.strip() else "A"
    live_pdf = generate_ticket_bytes(
        pdf_client,
        st.session_state.cart,
        total_general,
        st.session_state.observaciones_input
    )

    st.download_button(
        "🎟️ Descargar Comprobante",
        data=live_pdf,
        file_name=f"ticket_de_{client_name}.pdf",
        mime="application/pdf"
    )

    # --------------------------------------------------------
    #  💾 GUARDAR / ACTUALIZAR
    # --------------------------------------------------------
    if st.button("💾 Guardar Venta"):
        sheets = get_sheets()

        sheets.append_sale(client_name, st.session_state.cart, st.session_state.observaciones_input)
        st.success("✔ Venta registrada correctamente")

        # Limpiar
        st.session_state.cart = []
        if "editing_id" in st.session_state:
            del st.session_state.editing_id

        st.rerun()
