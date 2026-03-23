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
            
            # 2. Extraer Precio (Busca el primer precio visible)
            precio_tag = libro.find('span', {'class': 'a-offscreen'})
            precio = precio_tag.text.strip() if precio_tag else "No disponible"
            
            # 3. EXTRACCIÓN AVANZADA DE RESEÑAS
            reseñas = 0
            
            # Intento A: La etiqueta clásica de texto subrayado
            reseñas_tag = libro.find('span', {'class': 'a-size-base s-underline-text'})
            if reseñas_tag:
                texto_limpio = re.sub(r'\D', '', reseñas_tag.text) # Extrae solo números
                if texto_limpio.isdigit():
                    reseñas = int(texto_limpio)
            
            # Intento B: Si el A falla, busca en los enlaces de reseñas de clientes
            if reseñas == 0:
                links = libro.find_all('a')
                for a in links:
                    if a.has_attr('href') and 'customerReviews' in a['href']:
                        span_texto = a.find('span', {'class': 'a-size-base'})
                        if span_texto:
                            texto_limpio = re.sub(r'\D', '', span_texto.text)
                            if texto_limpio.isdigit():
                                reseñas = int(texto_limpio)
                                break
            
            resultados.append({
                "Título": titulo,
                "Reseñas": reseñas,
                "Precio": precio
            })
            
        return resultados

    except Exception as e:
        return {"error": str(e)}
