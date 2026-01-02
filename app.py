import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
DB_FILE = "tickets.csv"
LOGO_FILE = "LOGO JECE MINIATURA.png" # Nombre exacto de tu archivo
PASSWORD_SECRETA = "admin123" 

def cargar_datos():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if "Solución" not in df.columns: df["Solución"] = ""
        if "Costo_USD" not in df.columns: df["Costo_USD"] = 0.0
        df["ID"] = df["ID"].astype(int)
        return df
    else:
        return pd.DataFrame(columns=["ID", "Fecha", "Cliente", "Categoría", "Prioridad", "Descripción", "Estado", "Solución", "Costo_USD"])

def guardar_datos(df):
    df.to_csv(DB_FILE, index=False)

def style_tickets(row):
    if row["Estado"] == "Resuelto":
        return ['background-color: #d4edda; color: #155724'] * len(row)
    elif row["Prioridad"] == "Urgente":
        return ['background-color: #f8d7da; color: #721c24; font-weight: bold'] * len(row)
    return [''] * len(row)

st.set_page_config(page_title="Jece Soluciones - Soporte", layout="wide")

# 1. BARRA LATERAL (LOGO JECE Y NUEVO TICKET)
with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)
    else:
        st.title("Jece Soluciones")
    
    st.divider()
    st.header("➕ Nuevo Ticket")
    with st.form("form_nuevo", clear_on_submit=True):
        cliente = st.text_input("Nombre del Cliente")
        cat = st.selectbox("Categoría", ["Mantenimiento", "Software", "Hardware", "Redes", "Cámaras"])
        prio = st.select_slider("Prioridad", options=["Baja", "Media", "Alta", "Urgente"])
        desc = st.text_area("Descripción del Problema")
        if st.form_submit_button("Registrar Ticket"):
            df = cargar_datos()
            nuevo_id = df["ID"].max() + 1 if not df.empty else 1
            nueva_fila = pd.DataFrame([{
                "ID": int(nuevo_id), "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Cliente": cliente, "Categoría": cat, "Prioridad": prio,
                "Descripción": desc, "Estado": "Abierto", "Solución": "Pendiente", "Costo_USD": 0.0
            }])
            df = pd.concat([df, nueva_fila], ignore_index=True)
            guardar_datos(df)
            st.success("Ticket registrado en Jece Soluciones")
            st.rerun()

# 2. MÉTRICAS DE NEGOCIO
st.title("🎫 Gestión de Soportes Técnicos")
df_tickets = cargar_datos()
ganancias = df_tickets[df_tickets["Estado"] == "Resuelto"]["Costo_USD"].sum()
c1, c2 = st.columns(2)
c1.metric("Tickets Resueltos", len(df_tickets[df_tickets["Estado"] == "Resuelto"]))
c2.metric("Ingresos Totales", f"$ {ganancias:,.2f} USD")

st.divider()

# 3. RESOLVER TICKET Y COBRO
st.subheader("🛠️ Finalizar Trabajo y Cobrar")
abiertos = df_tickets[df_tickets["Estado"] != "Resuelto"]
if not abiertos.empty:
    if "input_solucion" not in st.session_state: st.session_state.input_solucion = ""
    col_sel, col_sol, col_costo = st.columns([1, 2, 1])
    with col_sel:
        opciones = abiertos.apply(lambda x: f"ID {x['ID']} - {x['Cliente']}", axis=1).tolist()
        ticket_sel = st.selectbox("Seleccionar ticket:", opciones)
        id_actual = int(ticket_sel.split(" ")[1])
    with col_sol:
        texto_solucion = st.text_area("¿Qué solución se aplicó?", key="input_solucion")
    with col_costo:
        costo = st.number_input("Costo del servicio ($)", min_value=0.0, step=1.0)
    if st.button("✅ Registrar Solución y Cobro", use_container_width=True):
        if texto_solucion.strip() == "": st.error("Por favor describe la solución.")
        else:
            df_tickets.loc[df_tickets["ID"] == id_actual, ["Estado", "Solución", "Costo_USD"]] = ["Resuelto", texto_solucion, costo]
            guardar_datos(df_tickets)
            st.session_state.input_solucion = "" # Limpia la casilla
            st.success(f"Ticket #{id_actual} finalizado con éxito.")
            st.rerun()

st.divider()

# 4. HISTORIAL CON BUSCADOR
st.subheader("📋 Historial de Jece Soluciones")
busqueda = st.text_input("🔍 Buscar cliente, problema o solución...")
df_filt = df_tickets[df_tickets.apply(lambda r: r.astype(str).str.contains(busqueda, case=False).any(), axis=1)] if busqueda else df_tickets

st.dataframe(
    df_filt.sort_values(by="ID", ascending=False).style.apply(style_tickets, axis=1).format({"Costo_USD": "$ {:.2f}"}), 
    use_container_width=True
)

st.divider()

# 5. BORRADO SEGURO
with st.expander("🗑️ Borrar registro (Solo Administrador)"):
    col_del1, col_del2, col_del3 = st.columns([1, 1, 1])
    with col_del1:
        t_del = st.selectbox("Ticket a eliminar:", df_tickets.apply(lambda x: f"ID {x['ID']} - {x['Cliente']}", axis=1) if not df_tickets.empty else ["No hay tickets"])
    with col_del2:
        p_in = st.text_input("Clave de seguridad", type="password")
    with col_del3:
        st.write(" ")
        if st.button("🚨 Eliminar", use_container_width=True):
            if p_in == PASSWORD_SECRETA and not df_tickets.empty:
                id_b = int(t_del.split(" ")[1])
                df_tickets = df_tickets[df_tickets["ID"] != id_b]
                guardar_datos(df_tickets)
                st.rerun()
            else:
                st.error("Error en clave o datos.")