import requests
from bs4 import BeautifulSoup
import re

def buscar_en_amazon(palabra_clave, scraper_api_key):
    """
    Busca en Amazon utilizando ScraperAPI.
    """
    keyword_url = palabra_clave.replace(' ', '+')
    amazon_url = f"https://www.amazon.com/s?k={keyword_url}&i=stripbooks"
    
    payload = {
        'api_key': scraper_api_key,
        'url': amazon_url,
        'country_code': 'us'
    }

    try:
        # Aumentamos un poco el timeout por seguridad
        respuesta = requests.get('https://api.scraperapi.com/', params=payload, timeout=30)
        
        if respuesta.status_code != 200:
            return {"error": f"Fallo en ScraperAPI. Código: {respuesta.status_code}"}
            
        soup = BeautifulSoup(respuesta.content, 'html.parser')
        libros = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        resultados = []
        
        for libro in libros[:10]:
            # 1. Extraer Título
            titulo_tag = libro.find('h2')
            titulo = titulo_tag.text.strip() if titulo_tag else "Sin título"
            
            # 2. Extraer Precio (Manejo más seguro)
            precio = "N/A"
            precio_tag = libro.find('span', {'class': 'a-offscreen'})
            if precio_tag and '$' in precio_tag.text:
                precio = precio_tag.text.strip()
            
            # 3. NUEVA EXTRACCIÓN AGRESIVA DE RESEÑAS
            reseñas = 0
            
            # Estrategia 1: Buscar enlaces directos a las reseñas (suele contener el número exacto)
            review_tags = libro.find_all('a', href=re.compile(r'#customerReviews'))
            for tag in review_tags:
                texto_limpio = tag.text.strip().replace(',', '').replace('.', '') # Limpiar comas (ej: 1,234 -> 1234)
                if texto_limpio.isdigit():
                    reseñas = int(texto_limpio)
                    break
            
            # Estrategia 2: Fallback buscando el aria-label si la Estrategia 1 falla
            if reseñas == 0:
                etiquetas_span = libro.find_all('span')
                for span in etiquetas_span:
                    aria = span.get('aria-label', '').lower()
                    if 'rating' in aria or 'calificaciones' in aria or 'stars' in aria:
                        # Busca el texto hermano que suele tener el conteo
                        texto_conteo = span.find_next_sibling('span')
                        if texto_conteo:
                            aria_conteo = texto_conteo.get('aria-label', '')
                            limpio = re.sub(r'\D', '', aria_conteo)
                            if limpio.isdigit():
                                reseñas = int(limpio)
                                break

            resultados.append({
                "Título": titulo,
                "Reseñas": reseñas,
                "Precio": precio
            })
            
        return resultados

    except Exception as e:
        return {"error": str(e)}
