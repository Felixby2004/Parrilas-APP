import streamlit as st
import json
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
    #  🔍 BUSCAR VENTA POR ID
    # --------------------------------------------------------
    st.subheader("🔍 Buscar Venta para Editar")

    buscar_id = st.text_input("Ingrese ID de venta", key="buscar_id")

    if st.button("Buscar Venta"):
        sheets = get_sheets()

        if not buscar_id.strip().isdigit():
            st.error("❌ El ID debe ser numérico.")
            return

        venta = sheets.get_sale_by_id(buscar_id)

        if not venta:
            st.error("❌ Venta no encontrada")
        else:
            st.success("✔ Venta cargada para edición")

            # Guardamos el ID
            st.session_state.editing_id = buscar_id  

            # Primera fila tiene cliente y observaciones
            fila0 = venta[0]
            st.session_state.cliente_input = fila0["cliente"]
            st.session_state.observaciones_input = fila0.get("observaciones", "")

            # Convertir filas a carrito
            carrito = []
            for row in venta:
                carrito.append({
                    "name": row["producto"],
                    "qty": int(row["cantidad"]),
                    "unit_price": float(row["precio unitario"]),
                    "extra": float(row["extra"]),
                    "subtotal": float(row["precio total"])
                })

            st.session_state.cart = carrito

            st.rerun()

    # --------------------------------------------------------
    #  INDICADOR DE EDICIÓN
    # --------------------------------------------------------
    if "editing_id" in st.session_state:
        st.info(f"✏️ Editando venta ID: {st.session_state.editing_id}")

    # --------------------------------------------------------
    #  👤 CLIENTE
    # --------------------------------------------------------
    client_name = st.text_input("Nombre del Cliente", key="cliente_input")

    st.subheader("🍽️ Platos")
    plato_select = st.selectbox("Selecciona un plato", ["Seleccionar"] + list(PLATOS.keys()))
    papas = False
    taper = False

    if plato_select != "Seleccionar":
        col1, col2 = st.columns(2)
        with col1:
            papas = st.checkbox("Agregar Papas Fritas")
        with col2:
            taper = st.checkbox("Agregar Taper")

    cantidad_plato = st.number_input("Cantidad", min_value=0, value=0, step=1)

    if st.button("Agregar Plato al Carrito"):
        if plato_select == "Seleccionar" or cantidad_plato <= 0:
            st.warning("Selecciona plato y cantidad válida.")
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
    cantidad_bebida = st.number_input("Cantidad bebidas", min_value=0, value=0, step=1)

    if st.button("Agregar Bebida al Carrito"):
        if bebida_select == "Seleccionar" or cantidad_bebida <= 0:
            st.warning("Selecciona bebida y cantidad válida.")
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
    #  ✏️ OBSERVACIONES
    # --------------------------------------------------------
    observaciones = st.text_area("Observaciones", key="observaciones_input")

    st.markdown("---")
    st.subheader("🛒 Carrito de Compra")

    if not st.session_state.cart:
        st.info("Carrito vacío.")
        return

    # --------------------------------------------------------
    #  LISTADO CARRITO
    # --------------------------------------------------------
    total_general = 0
    for i, item in enumerate(list(st.session_state.cart)):
        col = st.columns([4,1,2,2,2,1])
        col[0].write(item["name"])
        col[1].write(item["qty"])
        col[2].write(f"S/. {item['unit_price']:.2f}")
        col[3].write(f"S/. {item['extra']:.2f}")
        col[4].write(f"S/. {item['subtotal']:.2f}")

        if col[5].button("🗑️", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

        total_general += item["subtotal"]

    st.write(f"### 💵 Total General: S/. {total_general:.2f}")

    # --------------------------------------------------------
    #  📄 PDF
    # --------------------------------------------------------
    live_pdf = generate_ticket_bytes(
        client_name if client_name.strip() else "A",
        st.session_state.cart,
        total_general,
        st.session_state.observaciones_input
    )

    st.download_button(
        "🎟️ Descargar Comprobante",
        data=live_pdf,
        file_name=f"ticket_{client_name}.pdf",
        mime="application/pdf"
    )

    # --------------------------------------------------------
    #  💾 GUARDAR / ACTUALIZAR
    # --------------------------------------------------------
    if st.button("💾 Guardar Venta"):
        sheets = get_sheets()

        # SI ES EDICIÓN → borrar y reinsertar
        if "editing_id" in st.session_state:
            sheets.delete_sale(st.session_state.editing_id)
            venta_id_usar = st.session_state.editing_id
        else:
            venta_id_usar = sheets._get_next_venta_id()

        sheets.append_sale(
            client_name,
            st.session_state.cart,
            st.session_state.observaciones_input
        )

        st.success("✔ Venta guardada correctamente")

        st.session_state.cart = []
        if "editing_id" in st.session_state:
            del st.session_state.editing_id

        st.rerun()
