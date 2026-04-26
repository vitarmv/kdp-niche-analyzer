import requests
from bs4 import BeautifulSoup
import re

def buscar_en_amazon(palabra_clave, scraper_api_key):
    """
    Busca en Amazon utilizando ScraperAPI para evitar bloqueos.
    """
    keyword_url = palabra_clave.replace(' ', '+')
    # Filtramos por el nodo de libros para mayor precisión
    amazon_url = f"https://www.amazon.com/s?k={keyword_url}&i=stripbooks"
    
    payload = {
        'api_key': scraper_api_key,
        'url': amazon_url,
        'country_code': 'us' # IP de USA para ver el mercado principal
    }

    try:
        respuesta = requests.get('https://api.scraperapi.com/', params=payload, timeout=30)
        
        if respuesta.status_code != 200:
            return {"error": f"ScraperAPI falló (Código {respuesta.status_code})"}
            
        soup = BeautifulSoup(respuesta.content, 'html.parser')
        libros = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        resultados = []
        for libro in libros[:10]:
            titulo_tag = libro.find('h2')
            titulo = titulo_tag.text.strip() if titulo_tag else "Sin título"
            
            precio_tag = libro.find('span', {'class': 'a-offscreen'})
            precio = precio_tag.text.strip() if precio_tag else "N/A"
            
            # Extracción de reseñas mediante el atributo aria-label
            reseñas = 0
            etiquetas_span = libro.find_all('span')
            for span in etiquetas_span:
                aria = span.get('aria-label', '').lower()
                if 'rating' in aria or 'calificaciones' in aria:
                    texto_limpio = re.sub(r'\D', '', aria)
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
