import requests
from bs4 import BeautifulSoup
import re

def buscar_en_amazon(palabra_clave, scraper_api_key):
    """
    Busca en Amazon utilizando ScraperAPI. Recibe la API key como parámetro por seguridad.
    """
    keyword_url = palabra_clave.replace(' ', '+')
    amazon_url = f"https://www.amazon.com/s?k={keyword_url}&i=stripbooks"
    
    payload = {
        'api_key': scraper_api_key,
        'url': amazon_url,
        'country_code': 'us'
    }

    try:
        respuesta = requests.get('https://api.scraperapi.com/', params=payload, timeout=20)
        
        if respuesta.status_code != 200:
            return {"error": f"Fallo en ScraperAPI. Código: {respuesta.status_code}"}
            
        soup = BeautifulSoup(respuesta.content, 'html.parser')
        libros = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        resultados = []
        
        for libro in libros[:10]:
            # 1. Extraer Título
            titulo_tag = libro.find('h2')
            titulo = titulo_tag.text.strip() if titulo_tag else "Sin título"
            
            # 2. Extraer Precio
            precio_tag = libro.find('span', {'class': 'a-offscreen'})
            precio = precio_tag.text.strip() if precio_tag else "No disponible"
            
            # 3. EXTRACCIÓN AGRESIVA DE RESEÑAS (Buscando en atributos ocultos)
            reseñas = 0
            
            # Estrategia Principal: Buscar en los atributos 'aria-label'
            etiquetas_span = libro.find_all('span')
            for span in etiquetas_span:
                aria = span.get('aria-label', '').lower()
                # Buscamos palabras clave en inglés (ScraperAPI usa IP de USA) o español
                if 'rating' in aria or 'calificaciones' in aria or 'evaluaciones' in aria:
                    texto_limpio = re.sub(r'\D', '', aria) # Limpia todo y deja solo los números
                    if texto_limpio.isdigit():
                        reseñas = int(texto_limpio)
                        break # Si lo encuentra, detiene la búsqueda para este libro
            
            # Fallback: Si no había aria-label, intenta la clase clásica
            if reseñas == 0:
                reseñas_tag = libro.find('span', {'class': 'a-size-base s-underline-text'})
                if reseñas_tag:
                    texto_limpio = re.sub(r'\D', '', reseñas_tag.text)
                    if texto_limpio.isdigit():
                        reseñas = int(texto_limpio)

            resultados.append({
                "Título": titulo,
                "Reseñas": reseñas,
                "Precio": precio
            })
            
        return resultados

    except Exception as e:
        return {"error": str(e)}
