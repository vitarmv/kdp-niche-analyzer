import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import json

# IMPORTANTE: Importamos tu módulo scraper
from scraper_amazon import buscar_en_amazon

# Configuración básica
st.set_page_config(page_title="KDP Analyzer - Océanos Azules", layout="wide")
st.title("🌊 Buscador de Océanos Azules KDP")

# Inicializar la memoria de Streamlit para no perder la tabla al hacer clic en otros botones
if "df_ideas" not in st.session_state:
    st.session_state.df_ideas = None

with st.sidebar:
    st.header("⚙️ Configuración Fase 1")
    api_key = st.text_input("Ingresa tu API Key de Gemini:", type="password")
    
    if not api_key:
        st.warning("Por favor, ingresa tu API Key para continuar.")
        st.stop()
    
    st.divider()
    macro_nicho = st.text_input("Macro-Nicho a explorar:", value="Ansiedad Infantil")
    cantidad = st.slider("Cantidad de ideas a generar", min_value=3, max_value=10, value=5)
    buscar_btn = st.button("1. Generar Oportunidades (IA)", type="primary")

# --- FASE 1: GENERACIÓN CON IA ---
if buscar_btn:
    with st.spinner(f"🧠 Analizando variables para '{macro_nicho}' con Gemini 2.5 Pro..."):
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"""
            Actúa como experto en Amazon KDP. Encuentra "Océanos Azules" para: "{macro_nicho}".
            Genera {cantidad} ideas de subnichos (long-tail keywords).
            Devuelve ÚNICAMENTE un array JSON válido. Estructura exacta:
            [
              {{
                "palabra_clave_sugerida": "keyword",
                "angulo_diferenciador": "diferencia",
                "formato_ideal": "formato",
                "perfil_competidor_a_vencer": "debilidad"
              }}
            ]
            """
            response = client.models.generate_content(
                model='gemini-2.5-pro',
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.7, response_mime_type="application/json")
            )
            
            # Guardamos los datos en la memoria de la sesión
            datos = json.loads(response.text)
            st.session_state.df_ideas = pd.DataFrame(datos)
            st.success("¡Ideas generadas!")
            
        except Exception as e:
            st.error(f"Error en la IA: {e}")

# Mostrar la tabla si existe en memoria
if st.session_state.df_ideas is not None:
    st.subheader("💡 Oportunidades Detectadas")
    st.dataframe(st.session_state.df_ideas, hide_index=True, use_container_width=True)

    st.divider()

    # --- FASE 2: EXTRACCIÓN DE AMAZON ---
    st.subheader("📊 Fase 2: Validar en Mercado Real (Amazon)")
    st.markdown("Selecciona una palabra clave de la tabla superior para extraer los datos de sus competidores en la primera página de Amazon.")
    
    # Creamos un menú desplegable con las palabras clave generadas
    lista_keywords = st.session_state.df_ideas['palabra_clave_sugerida'].tolist()
    keyword_seleccionada = st.selectbox("Selecciona el nicho a validar:", lista_keywords)
    
    validar_btn = st.button("2. Extraer Datos de Amazon")
    
    if validar_btn:
        with st.spinner(f"🕵️‍♂️ Simulando navegación humana en Amazon para: '{keyword_seleccionada}'..."):
            
            # Llamamos a la función de tu archivo scraper_amazon.py
            resultados_amazon = buscar_en_amazon(keyword_seleccionada)
            
            if isinstance(resultados_amazon, dict) and "error" in resultados_amazon:
                st.error(f"⚠️ Hubo un problema con la extracción: {resultados_amazon['error']}")
                st.info("Nota: Si recibes el error 503, Amazon detectó que somos un bot. Intenta de nuevo en unos minutos.")
            
            elif isinstance(resultados_amazon, list) and len(resultados_amazon) > 0:
                st.success("¡Extracción completada con éxito!")
                df_amazon = pd.DataFrame(resultados_amazon)
                
                # Mostramos los resultados del scraper
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.dataframe(df_amazon, hide_index=True, use_container_width=True)
                with col2:
                    st.metric(label="Competidores Analizados", value=len(df_amazon))
                    # Calculamos un promedio rápido de reseñas si los datos son válidos
                    promedio_reseñas = df_amazon[df_amazon['Reseñas'] > 0]['Reseñas'].mean()
                    st.metric(label="Promedio de Reseñas (Top 10)", value=f"{promedio_reseñas:.0f}" if pd.notna(promedio_reseñas) else "0")
            else:
                st.warning("No se encontraron resultados para esta búsqueda o Amazon bloqueó la vista.")
