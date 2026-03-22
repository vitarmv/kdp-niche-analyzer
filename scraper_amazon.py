import requests
from bs4 import BeautifulSoup
import pandas as pd

def buscar_en_amazon(palabra_clave):
    """
    Busca en Amazon utilizando ScraperAPI para evadir el error 503.
    """
    # 1. Preparamos la URL de Amazon
    keyword_url = palabra_clave.replace(' ', '+')
    amazon_url = f"https://www.amazon.com/s?k={keyword_url}&i=stripbooks"
    
    # 2. Tu API Key de ScraperAPI (Pega tu clave real aquí)
    SCRAPERAPI_KEY = "d5e46a0bd2af0cde693ed63fac2e77e0"
    
    # 3. Configuramos la petición para que pase por el túnel
    payload = {
        'api_key': SCRAPERAPI_KEY,
        'url': amazon_url,
        'country_code': 'us' # Forzamos a que busque en Amazon USA
    }

    try:
        # Hacemos la petición a ScraperAPI, no directamente a Amazon
        # Le damos un timeout de 20 segundos porque a veces los proxies tardan un poco
        respuesta = requests.get('https://api.scraperapi.com/', params=payload, timeout=20)
        
        if respuesta.status_code != 200:
            return {"error": f"Fallo en ScraperAPI. Código: {respuesta.status_code}"}
            
        # Analizamos el HTML que nos devolvió ScraperAPI
        soup = BeautifulSoup(respuesta.content, 'html.parser')
        
        # Buscamos los libros
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
