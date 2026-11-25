"""Plantilla mínima de aplicación Streamlit: hipotecas sobre viviendas por provincia.

Ejecutar desde la carpeta principal del proyecto:

    uv run streamlit run apps/app_plantilla.py
"""
import pandas as pd
import plotly.express as px
import streamlit as st

st.title("Hipotecas sobre viviendas por provincia")
st.caption("Fuente: INE, Estadística de Hipotecas. Consulta datos/ORIGEN.md para saber si el fichero es real o simulado.")

# 1. Leer
hipotecas = pd.read_csv("datos/hipotecas.csv", dtype={"cod_prov": str}, parse_dates=["fecha"])

# 2. Controles
provincias = sorted(hipotecas["provincia"].unique())
elegidas = st.sidebar.multiselect("Provincias", provincias, default=["Salamanca", "Granada"])
suavizar = st.sidebar.checkbox("Media móvil de 12 meses", value=True)

# 3. Filtrar
datos = hipotecas[hipotecas["provincia"].isin(elegidas)].copy()
if suavizar:
    datos["hipotecas"] = datos.groupby("provincia")["hipotecas"].transform(lambda s: s.rolling(12).mean())

# 4. Dibujar
if datos.empty:
    st.info("Elige al menos una provincia.")
else:
    grafico = px.line(datos, x="fecha", y="hipotecas", color="provincia",
                      labels={"fecha": "", "hipotecas": "Hipotecas al mes", "provincia": "Provincia"})
    st.plotly_chart(grafico)
