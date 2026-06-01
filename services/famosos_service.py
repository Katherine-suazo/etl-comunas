import requests
from urllib.parse import quote
from datetime import datetime


def obtener_info_famoso(nombre):
    try:
        nombre = quote(nombre)
        url = (f"https://es.wikipedia.org/api/rest_v1/page/summary/{nombre}")

        headers = {"User-Agent": "ETL-Comunas/1.0"}
        response = requests.get(url, headers=headers, timeout=10)

        print("URL:", url)
        print("STATUS:", response.status_code)
        print("RESPUESTA:", response.text[:300])

        if response.status_code != 200:
            return None

        data = response.json()

        return {
            "nombre": data.get("title"),
            "descripcion": data.get("extract"),
            "imagen": data.get("thumbnail", {}).get("source"),
            "fuente": data.get("content_urls", {}).get("desktop", {}).get("page"),
            "fecha_captura": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }

    except Exception as e:
        print("ERROR FAMOSO:", e)
        return None