from datetime import datetime
from unidecode import unidecode
import re


# normalizar texto
def normalizar_texto(texto):
    texto = texto.strip()
    texto = unidecode(texto)
    texto = " ".join(texto.split())
    return texto


# normalizar fecha
def normalizar_fecha(fecha_texto):
    fecha_texto = fecha_texto.strip()
    formatos = ["%Y/%m/%d", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"]

    for formato in formatos:
        try:
            fecha = datetime.strptime(fecha_texto, formato)
            fecha_chile = fecha.strftime("%d-%m-%Y")
            return fecha_chile, fecha
        except:
            pass

    return None, None


# calcular edad
def calcular_edad(fecha):
    hoy = datetime.now()
    edad = hoy.year - fecha.year

    if (hoy.month, hoy.day) < (fecha.month, fecha.day):
        edad -= 1

    return edad


# detectar cumpleaños
def es_cumple(fecha):
    hoy = datetime.now()
    return (fecha.day == hoy.day and fecha.month == hoy.month)


# separar persona y fecha
def separar_persona_y_fecha(linea):
    match = re.match(
        r"^\s*\d+\.\s*(.+?)\s*(?:-|_|/|;|:|,|\s{2,})\s*(.+)\s*$",
        linea.strip()
    )

    if not match:
        return None, None

    nombre = match.group(1).strip()
    fecha = match.group(2).strip()
    return nombre, fecha


# extraer número y calle
def extraer_numero_y_calle(texto):
    texto = texto.strip()
    match_inicio = re.match(r"^(\d+[A-Za-z\-]*)\s+(.*)$", texto)

    if match_inicio:
        return match_inicio.group(2).strip(), match_inicio.group(1).strip()

    match_fin = re.match(r"^(.*?\b)(\d+[A-Za-z\-]*)$", texto)

    if match_fin:
        calle = match_fin.group(1).strip(" ,")
        numero = match_fin.group(2).strip()
        if calle:
            return calle, numero

    return texto, ""


# descomponer dirección
def descomponer_direccion(direccion):
    direccion_partes = [x.strip() for x in direccion.split(",") if x.strip()]

    nombre_calle = ""
    numero = ""
    ciudad_estado = ""
    pais = ""

    if not direccion_partes:
        return nombre_calle, numero, ciudad_estado, pais

    if len(direccion_partes) == 1:
        nombre_calle = direccion_partes[0]
        return nombre_calle, numero, ciudad_estado, pais

    pais = direccion_partes[-1]
    sin_pais = direccion_partes[:-1]

    if len(sin_pais) == 1:
        nombre_calle, numero = extraer_numero_y_calle(sin_pais[0])
        return nombre_calle, numero, ciudad_estado, pais

    primera = sin_pais[0]
    segunda = sin_pais[1]

    primera_tiene_numero = re.search(r"\d", primera) is not None
    segunda_empieza_numero = re.match(r"^\d+[A-Za-z\-]*\s+", segunda) is not None
    segunda_es_solo_numero = re.match(r"^\d+[A-Za-z\-]*$", segunda) is not None

    if not primera_tiene_numero and (segunda_empieza_numero or segunda_es_solo_numero):
        nombre_calle, numero = extraer_numero_y_calle(segunda)
        if not numero and segunda_es_solo_numero:
            numero = segunda
            nombre_calle = primera
        else:
            nombre_calle = f"{primera}, {nombre_calle}".strip(" ,")
    else:
        nombre_calle, numero = extraer_numero_y_calle(primera)
        if len(sin_pais) > 1:
            ciudad_estado = ", ".join(sin_pais[1:])
            return nombre_calle, numero, ciudad_estado, pais

    if len(sin_pais) > 2:
        ciudad_estado = ", ".join(sin_pais[2:])

    return nombre_calle, numero, ciudad_estado, pais


