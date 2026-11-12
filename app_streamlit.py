# app_streamlit.py
import streamlit as st
from pathlib import Path
from core.lector_excel import LectorExcel
from core.validador import Validador
from core.generador_pdf import GeneradorPDF
from config import obtener_config

st.set_page_config(page_title="Sistema Liquidaciones", layout="wide")
st.title("💼 Sistema Automatizado de Liquidaciones de Sueldo")

# Cargar configuración inicial
try:
    cfg = obtener_config()
except Exception as e:
    cfg = {}

uploaded_file = st.file_uploader("Subir Excel de remuneraciones", type=["xlsx"])

if uploaded_file:
    st.success("¡Archivo subido exitosamente!")
    
    # Instancias de los módulos principales
    lector = LectorExcel(uploaded_file)
    validador = Validador()
    
    try:
        df = lector.leer_datos()
        st.write("Vista previa de los datos cargados:", df.head())
        
        if validador.validar_datos(df):
            st.info("¡Los datos son válidos para procesar las liquidaciones!")
    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")