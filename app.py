import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import json

# 1. Configuración básica de la página
st.set_page_config(page_title="KDP Analyzer - Océanos Azules", layout="wide")

st.title("🌊 Buscador de Océanos Azules KDP")
st.markdown("Generador de subnichos hiper-específicos usando Inteligencia Artificial (Gemini 2.5 Pro).")

# 2. Panel lateral para configuración e inputs
with st.sidebar:
    st.header("Configuración")
    
    # Pedimos la API Key por pantalla
    api_key = st.text_input("Ingresa tu API Key de Gemini:", type="password")
    
    if not api_key:
        st.warning("Por favor, ingresa tu API Key de AI Studio para continuar.")
        st.stop()
    
    st.divider()
    
    # Inputs de búsqueda
    macro_nicho = st.text_input("Macro-Nicho a explorar:", value="Ansiedad Infantil")
    cantidad = st.slider("Cantidad de ideas a generar", min_value=3, max_value=15, value=5)
    buscar_btn = st.button("Buscar Oportunidades", type="primary")

# 3. Lógica principal al presionar el botón
if buscar_btn:
    with st.spinner(f"🧠 Analizando variables de mercado para '{macro_nicho}' con Gemini 2.5 Pro..."):
        try:
            # Inicializamos el cliente con la nueva librería
            client = genai.Client(api_key=api_key)
            
            # El Prompt maestro forzando la estructura JSON
            prompt = f"""
            Actúa como un experto en análisis de datos de Amazon KDP.
            Quiero encontrar "Océanos Azules" para el macro-nicho: "{macro_nicho}".
            
            Genera {cantidad} ideas de subnichos (long-tail keywords) cruzando variables como demografía, problemas específicos y formatos de publicación.
            
            CRÍTICO: Devuelve ÚNICAMENTE un array JSON válido, sin texto markdown. Estructura exacta:
            [
              {{
                "palabra_clave_sugerida": "ejemplo de keyword",
                "angulo_diferenciador": "por qué esto es diferente",
                "formato_ideal": "ej. Tapa Blanda (Libro de Trabajo)",
                "perfil_competidor_a_vencer": "qué debilidades tendrían los competidores actuales"
              }}
            ]
            """
            
            # Llamamos al modelo 2.5 Pro
            response = client.models.generate_content(
                model='gemini-2.5-pro',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    response_mime_type="application/json",
                )
            )
            
            # Procesamos la respuesta JSON a un formato tabular de Python
            datos = json.loads(response.text)
            df = pd.DataFrame(datos)
            
            st.success("¡Análisis completado con éxito!")
            
            # Mostramos la tabla interactiva
            st.dataframe(
                df,
                column_config={
                    "palabra_clave_sugerida": st.column_config.TextColumn("Palabra Clave", width="medium"),
                    "angulo_diferenciador": st.column_config.TextColumn("Ángulo Diferenciador", width="medium"),
                    "formato_ideal": st.column_config.TextColumn("Formato Sugerido", width="small"),
                    "perfil_competidor_a_vencer": st.column_config.TextColumn("Debilidad Competitiva", width="medium"),
                },
                hide_index=True,
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"Ocurrió un error al procesar los datos: {e}")