from google import genai

# ¡Reemplaza el texto entre comillas con tu clave real!
API_KEY = "AIzaSyBtoo_v_MN3MLb8VaotV2CFpB3GwgeAdC0"

print("🔍 Buscando modelos disponibles en tu cuenta...\n")

try:
    # Iniciamos el cliente con la nueva librería
    client = genai.Client(api_key=API_KEY)
    
    # Listamos los modelos
    for model in client.models.list():
        print(f"✅ {model.name}")
            
except Exception as e:
    print(f"❌ Error al consultar la API: {e}")
