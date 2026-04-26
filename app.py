import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import json

st.set_page_config(page_title="Generador de Océanos Azules KDP", layout="wide")
st.title("🌊 KDP Blue Ocean Generator")
st.markdown("Generador avanzado de ángulos diferenciadores y micro-nichos.")

if "df_ideas" not in st.session_state:
    st.session_state.df_ideas = None

with st.sidebar:
    st.header("🔑 Credenciales")
    api_key_gemini = st.text_input("API Key de Gemini:", type="password")
    
    if not api_key_gemini:
        st.warning("⚠️ Ingresa tu clave para habilitar la IA.")
        st.stop()
    
    st.divider()
    st.header("⚙️ Configuración Estratégica")
    
    mercado_objetivo = st.radio(
        "Mercado a explorar:",
        ["🇺🇸 Estados Unidos (Inglés)", "🇪🇸🌎 Hispano (Español)"]
    )
    
    macro_nicho = st.text_input("Macro-Nicho a explorar:", value="Ansiedad Infantil")
    cantidad = st.slider("Cantidad de nichos a generar", min_value=3, max_value=15, value=7)
    buscar_btn = st.button("🚀 Generar Océanos Azules", type="primary")

# --- FASE ÚNICA: GENERACIÓN AVANZADA ---
if buscar_btn:
    if mercado_objetivo == "🇺🇸 Estados Unidos (Inglés)":
        idioma = "INGLÉS"
        contexto = "Amazon.com (Mercado US)"
    else:
        idioma = "ESPAÑOL"
        contexto = "Mercado de habla hispana (Amazon.es / Amazon.com.mx)"

    with st.spinner(f"🧠 Explotando el modelo Gemini 3.1 Pro para '{macro_nicho}'..."):
        try:
            client = genai.Client(api_key=api_key_gemini)
            
            # EL PROMPT LETAL
            prompt = f"""
            Actúa como un estratega de élite en Amazon KDP y marketing orgánico.
            Tu misión es encontrar "Océanos Azules" altamente rentables y sin explotar para el macro-nicho: "{macro_nicho}".
            El mercado objetivo es: {contexto}.
            
            No me des ideas genéricas. Busca intersecciones extrañas (ej. "TDAH + Finanzas Personales").
            Genera {cantidad} ideas de micro-nichos.
            
            IMPORTANTE: Devuelve ÚNICAMENTE un array JSON válido. Los valores generados deben estar OBLIGATORIAMENTE en {idioma}.
            Estructura exacta del JSON:
            [
              {{
                "long_tail_keyword": "palabra clave exacta de baja competencia",
                "subtitulo_gancho": "un subtítulo magnético optimizado para SEO en KDP",
                "angulo_psicologico": "por qué el cliente DESEA comprar esto (ej. alivio de culpa, necesidad de control, estatus)",
                "perfil_competidor_a_vencer": "qué están haciendo mal los libros actuales de la primera página",
                "formato_ideal": "ej. Workbook interactivo / Diario guiado / Libro de actividades"
              }}
            ]
            """
            
            response = client.models.generate_content(
                model='models/gemini-3.1-pro-preview', # Usando el modelo más avanzado de tu lista
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.8, # Un poco más alto para mayor creatividad lateral
                    response_mime_type="application/json"
                )
            )
            
            datos = json.loads(response.text)
            st.session_state.df_ideas = pd.DataFrame(datos)
            st.success(f"¡Análisis profundo completado para el mercado en {idioma}!")
        except Exception as e:
            st.error(f"Error de ejecución: {e}")

# --- VISUALIZACIÓN DE DATOS ---
if st.session_state.df_ideas is not None:
    st.subheader("💡 Micro-Nichos de Alta Rentabilidad")
    st.dataframe(st.session_state.df_ideas, hide_index=True, use_container_width=True)
    
    st.info("📌 **Siguiente paso:** Copia la 'long_tail_keyword' de los resultados que más te llamen la atención y valídalos directamente en Amazon usando tu extensión Titans Quick View.")
