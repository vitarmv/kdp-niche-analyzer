import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import json

from scraper_amazon import buscar_en_amazon

st.set_page_config(page_title="KDP Analyzer - Océanos Azules", layout="wide")
st.title("🌊 Buscador de Océanos Azules KDP")

if "df_ideas" not in st.session_state:
    st.session_state.df_ideas = None

with st.sidebar:
    st.header("🔑 Credenciales")
    api_key_gemini = st.text_input("API Key de Gemini:", type="password")
    api_key_scraper = st.text_input("API Key de ScraperAPI:", type="password")
    
    if not api_key_gemini or not api_key_scraper:
        st.warning("⚠️ Ingresa ambas claves para habilitar el sistema.")
        st.stop()
    
    st.divider()
    st.header("⚙️ Configuración")
    
    # NUEVO: Selector de mercado objetivo
    mercado_objetivo = st.radio(
        "Mercado a explorar:",
        ["🇺🇸 Estados Unidos (Inglés)", "🇪🇸🌎 Hispano (Español)"]
    )
    
    macro_nicho = st.text_input("Macro-Nicho a explorar:", value="Ansiedad Infantil")
    cantidad = st.slider("Cantidad de ideas", min_value=3, max_value=10, value=5)
    buscar_btn = st.button("1. Generar Oportunidades (IA)", type="primary")

# --- FASE 1: GENERACIÓN CON GEMINI 2.5 PRO BILINGÜE ---
if buscar_btn:
    # Definimos variables dinámicas según el mercado elegido
    if mercado_objetivo == "🇺🇸 Estados Unidos (Inglés)":
        idioma_salida = "INGLÉS"
        contexto_mercado = "Amazon.com (Mercado de Estados Unidos)"
    else:
        idioma_salida = "ESPAÑOL"
        contexto_mercado = "Amazon.es y Amazon.com.mx (Mercado de habla hispana)"

    with st.spinner(f"🧠 Analizando el mercado {contexto_mercado} para '{macro_nicho}'..."):
        try:
            client = genai.Client(api_key=api_key_gemini)
            
            # El prompt ahora se adapta automáticamente al idioma y mercado
            prompt = f"""
            Actúa como experto en Amazon KDP y estrategia de nichos. 
            El usuario te dará un macro-nicho: "{macro_nicho}".
            Tu tarea es encontrar "Océanos Azules" reales (baja competencia, alta demanda) enfocados 100% en el mercado objetivo: {contexto_mercado}.
            Genera {cantidad} ideas de subnichos específicos (long-tail keywords).
            
            IMPORTANTE: Devuelve ÚNICAMENTE un array JSON válido. Estructura exacta (los valores generados deben estar obligatoriamente en {idioma_salida}):
            [
              {{
                "palabra_clave_sugerida": "long-tail keyword en {idioma_salida}",
                "angulo_diferenciador": "cómo destaca el libro en {idioma_salida}",
                "formato_ideal": "formato sugerido en {idioma_salida}",
                "perfil_competidor_a_vencer": "debilidad común de la competencia en {idioma_salida}"
              }}
            ]
            """
            
            response = client.models.generate_content(
                model='models/gemini-2.5-pro',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7, 
                    response_mime_type="application/json"
                )
            )
            
            datos = json.loads(response.text)
            st.session_state.df_ideas = pd.DataFrame(datos)
            st.success(f"¡Ideas generadas exitosamente para el mercado en {idioma_salida}!")
        except Exception as e:
            st.error(f"Error en la IA: {e}")

# --- FASE 2: EXTRACCIÓN Y VALIDACIÓN ---
if st.session_state.df_ideas is not None:
    st.subheader("💡 Oportunidades Detectadas")
    st.dataframe(st.session_state.df_ideas, hide_index=True, use_container_width=True)

    st.divider()
    st.subheader("📊 Fase 2: Validar Datos Reales de Amazon")
    
    modo_busqueda = st.radio(
        "¿Cómo quieres buscar a los competidores?",
        ["Seleccionar de la tabla (IA)", "Escribir búsqueda manual"],
        horizontal=True
    )
    
    if modo_busqueda == "Seleccionar de la tabla (IA)":
        lista_keywords = st.session_state.df_ideas['palabra_clave_sugerida'].tolist()
        keyword_seleccionada = st.selectbox("Selecciona el nicho a validar:", lista_keywords)
    else:
        keyword_seleccionada = st.text_input("Escribe la palabra clave exacta:")
    
    validar_btn = st.button("2. Extraer Datos de Amazon")
    
    if validar_btn:
        if not keyword_seleccionada.strip():
            st.warning("⚠️ Ingresa una palabra clave.")
        else:
            with st.spinner(f"🕵️‍♂️ Scraper activado para: '{keyword_seleccionada}'..."):
                resultados_amazon = buscar_en_amazon(keyword_seleccionada, api_key_scraper)
                
                if isinstance(resultados_amazon, dict) and "error" in resultados_amazon:
                    st.error(f"⚠️ Error de extracción: {resultados_amazon['error']}")
                elif isinstance(resultados_amazon, list) and len(resultados_amazon) > 0:
                    st.success("¡Datos extraídos!")
                    df_amazon = pd.DataFrame(resultados_amazon)
                    st.dataframe(df_amazon, hide_index=True, use_container_width=True)
                else:
                    st.warning("No se encontraron resultados en esta categoría.")
