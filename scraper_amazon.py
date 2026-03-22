import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

def buscar_en_amazon(palabra_clave):
    """
    Busca una palabra clave en la categoría de libros de Amazon y extrae 
    títulos, precios y cantidad de reseñas de la primera página.
    """
    # Reemplazamos espacios por '+' para la URL
    keyword_url = palabra_clave.replace(' ', '+')
    url = f"https://www.amazon.com/s?k={keyword_url}&i=stripbooks"
    
    # CRÍTICO: Estos headers simulan ser un usuario humano en Windows navegando con Chrome
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.amazon.com/'
    }

    try:
        # Pausa aleatoria entre 1 y 3 segundos para parecer humano
        time.sleep(random.uniform(1, 3))
        
        respuesta = requests.get(url, headers=headers, timeout=10)
        
        # Si Amazon nos bloquea o pide CAPTCHA, el código de estado no será 200
        if respuesta.status_code != 200:
            return {"error": f"Bloqueado por Amazon. Código: {respuesta.status_code}"}
            
        soup = BeautifulSoup(respuesta.content, 'html.parser')
        
        # Buscamos todos los contenedores de productos en la página de resultados
        libros = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        resultados = []
        
        for libro in libros[:10]:  # Analizamos solo el Top 10
            # Extraer Título
            titulo_tag = libro.find('h2')
            titulo = titulo_tag.text.strip() if titulo_tag else "Sin título"
            
            # Extraer Reseñas (Cantidad)
            reseñas_tag = libro.find('span', {'class': 'a-size-base s-underline-text'})
            reseñas = reseñas_tag.text.strip().replace(',', '') if reseñas_tag else "0"
            
            # Extraer Precio
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

# Bloque de prueba local
if __name__ == "__main__":
    test_keyword = "ansiedad infantil workbook"
    print(f"Buscando: {test_keyword}...")
    datos = buscar_en_amazon(test_keyword)
    
    if isinstance(datos, list):
        df = pd.DataFrame(datos)
        print("\nResultados encontrados:")
        print(df)
    else:
        print("\nError detectado:", datos)
