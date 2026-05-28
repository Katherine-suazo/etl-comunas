import requests
from services.normalizador import (normalizar_texto)


BASE_URL = ("https://chileabierto.cl/api/v1/comunas")

def buscar_comuna_api(nombre_comuna):
    try:
        nombre_comuna = normalizar_texto(nombre_comuna)
        response = requests.get(BASE_URL, params={"search": nombre_comuna}, timeout=10)

        if response.status_code != 200:
            return []
        
        data = response.json()
        resultados = []

        for comuna in data["data"]:
            resultados.append({
                "comuna": comuna["name"],
                "region": comuna["region_name"],
                "provincia": comuna["province_name"],
                "habitantes": comuna["population"],
            })
        return resultados
    
    except Exception as e:
        print("ERROR API:", e)
        return []