import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURACIÓN Y ARCHIVOS ---
DB_FILE = "tickets.csv"

def cargar_datos():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if "Solución" not in df.columns:
            df["Solución"] = ""
        df["ID"] = df["ID"].astype(int)
        return df
    else:
        return pd.DataFrame(columns=["ID", "Fecha", "Cliente", "Categoría", "Prioridad", "Descripción", "Estado", "Solución"])

def guardar_datos(df):
    df.to_csv(DB_FILE, index=False)

# --- ESTILOS DE COLORES ---
def style_tickets(row):
    if row["Estado"] == "Resuelto":
        return ['background-color: #d4edda; color: #155724'] * len(row) # Verde
    elif row["Prioridad"] == "Urgente":
        return ['background-color: #f8d7da; color: #721c24; font-weight: bold'] * len(row) # Rojo
    elif row["Prioridad"] == "Alta":
        return ['background-color: #fff3cd; color: #856404'] * len(row) # Amarillo
    return [''] * len(row)

# --- INICIO DE LA APP ---
st.set_page_config(page_title="Soporte Técnico Pro", layout="wide")

# 1. LOGO Y NUEVO TICKET (Barra Lateral)
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.info("💡 Sube 'logo.png' a tu carpeta.")
    
    st.header("➕ Nuevo Ticket")
    with st.form("form_nuevo", clear_on_submit=True):
        cliente = st.text_input("Cliente")
        cat = st.selectbox("Categoría", ["Mantenimiento", "Software", "Hardware", "Redes"])
        prio = st.select_slider("Prioridad", options=["Baja", "Media", "Alta", "Urgente"])
        desc = st.text_area("Descripción del Problema")
        
        if st.form_submit_button("Registrar Ticket"):
            df = cargar_datos()
            nuevo_id = df["ID"].max() + 1 if not df.empty else 1
            nueva_fila = pd.DataFrame([{
                "ID": int(nuevo_id),
                "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Cliente": cliente, "Categoría": cat, "Prioridad": prio,
                "Descripción": desc, "Estado": "Abierto", "Solución": "Pendiente"
            }])
            df = pd.concat([df, nueva_fila], ignore_index=True)
            guardar_datos(df)
            st.success("¡Ticket Creado!")
            st.rerun()

# 2. PANEL DE RESOLUCIÓN (Cuerpo Principal)
st.title("🎫 Gestión de Soportes Técnicos")
df_tickets = cargar_datos()

st.subheader("🛠️ Resolver Ticket Pendiente")
abiertos = df_tickets[df_tickets["Estado"] != "Resuelto"]

if not abiertos.empty:
    # Usamos una clave (key) en el session_state para la solución
    if "input_solucion" not in st.session_state:
        st.session_state.input_solucion = ""

    col_sel, col_sol = st.columns([1, 2])
    
    with col_sel:
        lista_opciones = abiertos.apply(lambda x: f"ID {x['ID']} - {x['Cliente']}", axis=1).tolist()
        ticket_sel = st.selectbox("Seleccionar ticket:", lista_opciones)
        id_actual = int(ticket_sel.split(" ")[1])

    with col_sol:
        # El valor del area de texto se vincula a session_state
        texto_solucion = st.text_area("Solución aplicada:", key="input_solucion")
        
    if st.button("✅ Guardar Solución y Cerrar Ticket", use_container_width=True):
        if texto_solucion.strip() == "":
            st.error("Debes describir la solución antes de cerrar.")
        else:
            df_tickets.loc[df_tickets["ID"] == id_actual, "Estado"] = "Resuelto"
            df_tickets.loc[df_tickets["ID"] == id_actual, "Solución"] = texto_solucion
            guardar_datos(df_tickets)
            
            # ¡MAGIA AQUÍ! Limpiamos el texto para el siguiente
            st.session_state.input_solucion = "" 
            
            st.success(f"Ticket #{id_actual} cerrado con éxito.")
            st.rerun()
else:
    st.info("✅ Todos los tickets están al día.")

st.divider()

# 3. BUSCADOR E HISTORIAL
st.subheader("📋 Historial Completo")
busqueda = st.text_input("🔍 Buscar por cliente, problema o solución...")

df_filt = df_tickets
if busqueda:
    df_filt = df_tickets[df_tickets.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)]

if not df_filt.empty:
    st.dataframe(df_filt.sort_values(by="ID", ascending=False).style.apply(style_tickets, axis=1), use_container_width=True)
else:
    st.warning("No se encontraron registros.")