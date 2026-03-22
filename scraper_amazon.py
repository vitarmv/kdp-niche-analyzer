import requests
from bs4 import BeautifulSoup
import pandas as pd

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
            titulo_tag = libro.find('h2')
            titulo = titulo_tag.text.strip() if titulo_tag else "Sin título"
            
            reseñas_tag = libro.find('span', {'class': 'a-size-base s-underline-text'})
            reseñas = reseñas_tag.text.strip().replace(',', '') if reseñas_tag else "0"
            
            precio_tag = libro.find('span', {'class': 'a-offscreen'})
            precio = precio_tag.text.strip() if precio_tag else "No disponible"
            
            resultados.append({
                "Título": titulo,
                "Reseñas": int(reseñas) if reseñas.isdigit() else 0,
                "Precio": precio
            })
            
        return resultados

    except Exception as e:
        return {"error": str(e)}
