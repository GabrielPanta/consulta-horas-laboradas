import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv

# ======================
# CONFIGURACIÓN INICIAL
# ======================
st.set_page_config(page_title="Panel de Administración", layout="centered")
load_dotenv()

# Eliminar barra lateral (mejor para móviles)
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .block-container {padding-top: 1rem;}
    </style>
""", unsafe_allow_html=True)

# ======================
# CREDENCIALES
# ======================
ADMIN_VERFRUT_PASS = os.getenv("ADMIN_VERFRUT_PASS")
ADMIN_RAPEL_PASS = os.getenv("ADMIN_RAPEL_PASS")

# ======================
# SESIÓN
# ======================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "empresa" not in st.session_state:
    st.session_state.empresa = None

# ======================
# BASE DE DATOS
# ======================
conn = sqlite3.connect("asistencias.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS asistencias (
    dni TEXT,
    nombre TEXT,
    fecha TEXT,
    horas_trabajadas TEXT,
    mes TEXT,
    empresa TEXT,
    PRIMARY KEY (dni, fecha, empresa)
)
""")
conn.commit()

# ======================
# LOGIN ADMIN
# ======================
if not st.session_state.autenticado:
    st.title("🔐 Ingreso de Administrador")

    empresa = st.selectbox("Selecciona la empresa", ["VERFRUT", "RAPEL"])
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if empresa == "VERFRUT" and password == ADMIN_VERFRUT_PASS:
            st.session_state.autenticado = True
            st.session_state.empresa = "VERFRUT"
        elif empresa == "RAPEL" and password == ADMIN_RAPEL_PASS:
            st.session_state.autenticado = True
            st.session_state.empresa = "RAPEL"
        else:
            st.error("❌ Contraseña incorrecta o empresa no válida")

    if not st.session_state.autenticado:
        st.stop()

# ======================
# PANEL PRINCIPAL
# ======================
empresa = st.session_state.empresa
st.title(f"📊 Panel de Administración — {empresa}")

# Seleccionar mes
mes = st.selectbox("Selecciona el mes", [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
])

# Subir Excel
archivo = st.file_uploader("📁 Subir archivo Excel con asistencias", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    columnas_requeridas = ["IDTRABAJADOR", "APELLIDOPAT", "APELLIDOMAT", "NOMBRE","RUT"]
    if not all(col in df.columns for col in columnas_requeridas):
        st.error("⚠️ El archivo debe tener las columnas: IDTRABAJADOR, APELLIDOPAT, APELLIDOMAT, NOMBRE,RUT")
    else:
        # Convertir formato ancho a largo
        df_long = []
        for _, fila in df.iterrows():
            dni = str(fila["RUT"])
            nombre = f"{fila['APELLIDOPAT']} {fila['APELLIDOMAT']} {fila['NOMBRE']}".strip()
            for col in df.columns[5:]:
                valor = fila[col]
                if pd.notna(valor) and str(valor).strip() != "":
                    try:
                        dia = int(col)
                        numero_mes = [
                            "Enero","Febrero","Marzo","Abril","Mayo","Junio",
                            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
                        ].index(mes) + 1
                        fecha = f"2025-{str(numero_mes).zfill(2)}-{str(dia).zfill(2)}"
                    except:
                        fecha = str(col)
                    df_long.append((dni, nombre, fecha, str(valor), mes, empresa))

        df_final = pd.DataFrame(df_long, columns=["dni", "nombre", "fecha", "horas_trabajadas", "mes", "empresa"])

        # Guardar o actualizar datos
        with conn:
            for _, row in df_final.iterrows():
                cursor.execute("""
                INSERT INTO asistencias (dni, nombre, fecha, horas_trabajadas, mes, empresa)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(dni, fecha, empresa) DO UPDATE SET
                    nombre = excluded.nombre,
                    horas_trabajadas = excluded.horas_trabajadas,
                    mes = excluded.mes
                """, tuple(row))
            conn.commit()

        st.success(f"✅ Datos importados y actualizados correctamente para {empresa}")

# Mostrar últimos registros
st.subheader(f"📋 Últimos registros de {empresa}")
df_mostrar = pd.read_sql_query(f"""
SELECT dni, nombre, fecha, horas_trabajadas, mes 
FROM asistencias 
WHERE empresa = '{empresa}'
ORDER BY fecha DESC 
LIMIT 20
""", conn)
st.dataframe(df_mostrar, use_container_width=True)

# Botón de cerrar sesión
if st.button("🔒 Cerrar sesión"):
    st.session_state.autenticado = False
    st.session_state.empresa = None
    st.rerun()





