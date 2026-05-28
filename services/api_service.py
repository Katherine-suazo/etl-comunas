import requests
from services.normalizador import (normalizar_texto, aplicar_formato)


BASE_URL = ("https://chileabierto.cl/api/v1/comunas")

def buscar_comuna_api(nombre_comuna, formato):
    try:
        nombre_comuna = normalizar_texto(nombre_comuna)
        response = requests.get(BASE_URL, params={"search": nombre_comuna}, timeout=10)

        if response.status_code != 200:
            return []
        
        data = response.json()
        resultados = []

        for comuna in data["data"]:
            resultados.append({
                "comuna": aplicar_formato(comuna["name"], formato),
                "region": aplicar_formato(comuna["region_name"], formato),
                "provincia": aplicar_formato(comuna["province_name"], formato),
                "habitantes": comuna["population"],
            })
        return resultados
    
    except Exception as e:
        print("ERROR API:", e)
        return []