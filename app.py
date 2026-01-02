import streamlit as st
import pandas as pd
import os
from datetime import datetime

DB_FILE = "tickets.csv"

def cargar_datos():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if "Solución" not in df.columns:
            df["Solución"] = ""
        # Aseguramos que el ID sea entero
        df["ID"] = df["ID"].astype(int)
        return df
    else:
        return pd.DataFrame(columns=["ID", "Fecha", "Cliente", "Categoría", "Prioridad", "Descripción", "Estado", "Solución"])

def guardar_datos(df):
    df.to_csv(DB_FILE, index=False)

# --- FUNCIÓN PARA COLOREAR FILAS ---
def style_tickets(row):
    # Color por Estado
    if row["Estado"] == "Resuelto":
        return ['background-color: #d4edda; color: #155724'] * len(row) # Verde claro
    # Color por Prioridad si está abierto
    elif row["Prioridad"] == "Urgente":
        return ['background-color: #f8d7da; color: #721c24; font-weight: bold'] * len(row) # Rojo claro
    elif row["Prioridad"] == "Alta":
        return ['background-color: #fff3cd; color: #856404'] * len(row) # Amarillo claro
    return [''] * len(row)

st.set_page_config(page_title="Soporte Técnico Pro", layout="wide")
st.title("🎫 Sistema de Registro de Tickets")

df_tickets = cargar_datos()

# --- BARRA LATERAL: CREACIÓN ---
with st.sidebar:
    st.header("Nuevo Ticket")
    with st.form("nuevo_ticket", clear_on_submit=True):
        cliente = st.text_input("Cliente")
        categoria = st.selectbox("Categoría", ["Mantenimiento", "Software", "Hardware", "Redes"])
        prioridad = st.select_slider("Prioridad", options=["Baja", "Media", "Alta", "Urgente"])
        descripcion = st.text_area("Descripción del Problema")
        
        if st.form_submit_button("Guardar Ticket"):
            nuevo_id = df_tickets["ID"].max() + 1 if not df_tickets.empty else 1
            nueva_fila = pd.DataFrame([{
                "ID": int(nuevo_id),
                "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Cliente": cliente, "Categoría": categoria,
                "Prioridad": prioridad, "Descripción": descripcion, 
                "Estado": "Abierto", "Solución": "Pendiente"
            }])
            df_tickets = pd.concat([df_tickets, nueva_fila], ignore_index=True)
            guardar_datos(df_tickets)
            st.success(f"Ticket #{nuevo_id} Creado")
            st.rerun()

# --- SECCIÓN: RESOLVER TICKET ---
st.subheader("🛠️ Finalizar Soporte Técnico")
tickets_abiertos = df_tickets[df_tickets["Estado"] != "Resuelto"]

if not tickets_abiertos.empty:
    with st.expander("Abrir panel de cierre", expanded=False):
        col_sel, col_sol = st.columns([1, 2])
        with col_sel:
            opciones = tickets_abiertos.apply(lambda x: f"ID {x['ID']} - {x['Cliente']}", axis=1).tolist()
            ticket_a_cerrar = st.selectbox("Selecciona ticket:", opciones)
            id_seleccionado = int(ticket_a_cerrar.split(" ")[1])
        with col_sol:
            solucion_texto = st.text_area("¿Cuál fue la solución aplicada?")
            
        if st.button("✅ Registrar Solución y Cerrar Ticket", use_container_width=True):
            if solucion_texto.strip() == "":
                st.error("Escribe la solución antes de cerrar.")
            else:
                df_tickets.loc[df_tickets["ID"] == id_seleccionado, "Estado"] = "Resuelto"
                df_tickets.loc[df_tickets["ID"] == id_seleccionado, "Solución"] = solucion_texto
                guardar_datos(df_tickets)
                st.success(f"Ticket #{id_seleccionado} resuelto.")
                st.rerun()

st.divider()

# --- TABLA CON ESTILO ---
st.subheader("📋 Historial de Soportes")
busqueda = st.text_input("🔍 Buscar por cliente o solución:")

if busqueda:
    df_mostrar = df_tickets[
        df_tickets['Cliente'].astype(str).str.contains(busqueda, case=False) | 
        df_tickets['Solución'].astype(str).str.contains(busqueda, case=False)
    ]
else:
    df_mostrar = df_tickets

# Aplicamos el estilo antes de mostrar la tabla
if not df_mostrar.empty:
    df_estilado = df_mostrar.sort_values(by="ID", ascending=False).style.apply(style_tickets, axis=1)
    st.dataframe(df_estilado, use_container_width=True)
else:
    st.info("Sin registros.")