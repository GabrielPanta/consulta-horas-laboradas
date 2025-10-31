import streamlit as st
import pandas as pd
import sqlite3

# ======================
# CONFIGURACIÓN INICIAL
# ======================
st.set_page_config(page_title="Consulta de Horas Laboradas", layout="centered")

# ======================
# BASE DE DATOS
# ======================
conn = sqlite3.connect("asistencias.db", check_same_thread=False)

# ======================
# PANEL DE CONSULTA
# ======================
st.title("🕒 Consulta de Horas Laboradas")

# Selección de empresa
empresa = st.selectbox("Selecciona tu empresa", ["VERFRUT", "RAPEL"])

# Ingreso de DNI
dni_input = st.text_input("Ingresa tu DNI").strip()

# Selección de mes
mes = st.selectbox("Selecciona el mes", [
    "Enero","Febrero","Marzo","Abril","Mayo","Junio",
    "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
])

if st.button("Consultar"):
    if dni_input == "":
        st.error("⚠️ Debes ingresar tu DNI")
    else:
        # Normalizamos el DNI: eliminamos espacios y decimales
        try:
            dni = str(int(float(dni_input)))
        except:
            dni = dni_input.strip()

        # Consulta segura en SQL, incluyendo nombre
        query = """
        SELECT nombre, fecha, horas_trabajadas
        FROM asistencias
        WHERE TRIM(dni) = ? 
          AND UPPER(empresa) = UPPER(?) 
          AND LOWER(mes) = LOWER(?)
        ORDER BY fecha
        """
        df = pd.read_sql_query(query, conn, params=(dni, empresa.strip(), mes.strip()))

        if df.empty:
            st.warning("❌ No se encontraron registros para tu DNI en este mes")
        else:
            # Mostrar detalle diario tal cual está, incluyendo letras
            st.subheader("📅 Horas por día")
            st.dataframe(df, use_container_width=True)

            # Calcular total solo de valores numéricos
            df["horas_num"] = pd.to_numeric(df["horas_trabajadas"], errors='coerce').fillna(0)
            total_horas = round(df["horas_num"].sum(), 2)
            
            # Mostrar nombre del trabajador
            nombre_trabajador = df["nombre"].iloc[0]
            st.success(f"🟢 Total de horas  {mes}: {total_horas} horas")







