from flask import Flask, render_template, request, send_file
import pymysql
from unidecode import unidecode
from datetime import datetime
from dotenv import load_dotenv
import os
import csv
import re

# cargar variables .env
load_dotenv()

app = Flask(__name__)


# =====================================================
# CONEXION MYSQL
# =====================================================

def conectar_db():

    return pymysql.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT")),
        connect_timeout=10
    )


# =====================================================
# NORMALIZAR TEXTO
# =====================================================

def normalizar_texto(texto):

    texto = texto.strip()

    texto = unidecode(texto)

    texto = " ".join(texto.split())

    return texto


# =====================================================
# NORMALIZAR FECHA
# =====================================================

def normalizar_fecha(fecha_texto):

    fecha_texto = fecha_texto.strip()

    formatos = [
        "%Y/%m/%d",
        "%Y-%m-%d"
    ]

    for formato in formatos:

        try:

            fecha = datetime.strptime(
                fecha_texto,
                formato
            )

            fecha_chile = fecha.strftime(
                "%d-%m-%Y"
            )

            return fecha_chile, fecha

        except:
            pass

    return None, None


# =====================================================
# CALCULAR EDAD
# =====================================================

def calcular_edad(fecha):

    hoy = datetime.now()

    edad = hoy.year - fecha.year

    if (hoy.month, hoy.day) < (fecha.month, fecha.day):

        edad -= 1

    return edad


# =====================================================
# DETECTAR CUMPLEAÑOS
# =====================================================

def es_cumple(fecha):

    hoy = datetime.now()

    return (
        fecha.day == hoy.day and
        fecha.month == hoy.month
    )


# =====================================================
# RUTA PRINCIPAL
# =====================================================

@app.route("/", methods=["GET", "POST"])
def index():

    mensaje = ""

    datos = []

    encabezados = []

    if request.method == "POST":

        connection = None
        cursor = None

        try:

            archivo = request.files["archivo"]

            if archivo.filename == "":

                mensaje = "Debe seleccionar un archivo."

                return render_template(
                    "index.html",
                    mensaje=mensaje,
                    datos=datos,
                    encabezados=encabezados
                )

            # =================================================
            # LEER ARCHIVO
            # =================================================

            try:

                contenido = archivo.read().decode(
                    "utf-8"
                )

            except:

                archivo.seek(0)

                contenido = archivo.read().decode(
                    "latin-1"
                )

            lineas = contenido.splitlines()

            # =================================================
            # MYSQL
            # =================================================

            connection = conectar_db()

            cursor = connection.cursor()

            # =================================================
            # CREAR TABLAS
            # =================================================

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS PERSONAS (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(255) UNIQUE,
                fecha_original VARCHAR(255),
                fecha_normalizada VARCHAR(20),
                edad INT,
                cumple_hoy BOOLEAN
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS LUGARES (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(255) UNIQUE
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS DIRECCIONES (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre_calle VARCHAR(255),
                numero_calle VARCHAR(50),
                ciudad_estado_provincia VARCHAR(255),
                pais VARCHAR(255)
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS GEOREFERENCIAS (
                id INT AUTO_INCREMENT PRIMARY KEY,
                latitud VARCHAR(50),
                longitud VARCHAR(50)
            )
            """)

            insertados = 0

            duplicados = 0

            # =================================================
            # DETECTAR ARCHIVO
            # =================================================

            # =================================================
            # ARCHIVO LUGARES
            # =================================================

            if "Georeferencia" in contenido:

                csv_nombre = "lugares_limpio.csv"

                with open(
                    csv_nombre,
                    "w",
                    newline="",
                    encoding="utf-8"
                ) as csvfile:

                    writer = csv.writer(csvfile)

                    writer.writerow([
                        "Lugar",
                        "Nombre Calle",
                        "Numero Calle",
                        "Ciudad/Estado",
                        "Pais",
                        "Latitud",
                        "Longitud"
                    ])

                    # saltar encabezado
                    for linea in lineas[1:]:

                        if linea.strip() == "":
                            continue

                        try:

                            partes = linea.split(";")

                            if len(partes) < 3:
                                continue

                            lugar = normalizar_texto(
                                partes[0]
                            )

                            direccion = partes[1].strip()

                            geo = partes[2].strip()

                            # validar georeferencia
                            if "," not in geo:
                                continue

                            geo_partes = geo.split(",")

                            if len(geo_partes) < 2:
                                continue

                            latitud = geo_partes[0].strip()

                            longitud = geo_partes[1].strip()

                            # =====================================
                            # DIRECCION
                            # =====================================

                            direccion_partes = [
                                x.strip()
                                for x in direccion.split(",")
                            ]

                            nombre_calle = ""

                            numero = ""

                            ciudad_estado = ""

                            pais = ""

                            if len(direccion_partes) == 1:

                                nombre_calle = (
                                    direccion_partes[0]
                                )

                            elif len(direccion_partes) >= 2:

                                pais = direccion_partes[-1]

                                primer_parte = (
                                    direccion_partes[0]
                                )

                                # detectar numero
                                match = re.match(
                                    r"^(\d+)\s+(.*)",
                                    primer_parte
                                )

                                if match:

                                    numero = match.group(1)

                                    nombre_calle = (
                                        match.group(2)
                                    )

                                else:

                                    nombre_calle = (
                                        primer_parte
                                    )

                                # ciudad / estado
                                if len(direccion_partes) > 2:

                                    ciudad_estado = ", ".join(
                                        direccion_partes[1:-1]
                                    )

                            # =====================================
                            # INSERT MYSQL
                            # =====================================

                            cursor.execute("""
                            INSERT IGNORE INTO LUGARES
                            (nombre)
                            VALUES (%s)
                            """, (lugar,))

                            cursor.execute("""
                            INSERT INTO DIRECCIONES
                            (
                                nombre_calle,
                                numero_calle,
                                ciudad_estado_provincia,
                                pais
                            )
                            VALUES (%s, %s, %s, %s)
                            """, (
                                nombre_calle,
                                numero,
                                ciudad_estado,
                                pais
                            ))

                            cursor.execute("""
                            INSERT INTO GEOREFERENCIAS
                            (
                                latitud,
                                longitud
                            )
                            VALUES (%s, %s)
                            """, (
                                latitud,
                                longitud
                            ))

                            # =====================================
                            # CSV
                            # =====================================

                            writer.writerow([
                                lugar,
                                nombre_calle,
                                numero,
                                ciudad_estado,
                                pais,
                                latitud,
                                longitud
                            ])

                            insertados += 1

                        except Exception as e:

                            print(
                                "ERROR LUGAR:",
                                e
                            )

                            duplicados += 1

                # =============================================
                # MOSTRAR DATOS
                # =============================================

                cursor.execute("""
                SELECT *
                FROM LUGARES
                """)

                datos = cursor.fetchall()

                encabezados = [
                    "ID",
                    "Nombre Lugar"
                ]

                mensaje = f"""
                Archivo de lugares procesado correctamente.

                Insertados: {insertados}

                Duplicados/Error: {duplicados}
                """

            # =================================================
            # ARCHIVO PERSONAS
            # =================================================

            else:

                csv_nombre = "personas_limpio.csv"

                with open(
                    csv_nombre,
                    "w",
                    newline="",
                    encoding="utf-8"
                ) as csvfile:

                    writer = csv.writer(csvfile)

                    writer.writerow([
                        "Nombre",
                        "Fecha Original",
                        "Fecha Normalizada",
                        "Edad",
                        "Cumple Hoy"
                    ])

                    for linea in lineas:

                        if linea.strip() == "":
                            continue

                        try:

                            partes = linea.split(" - ")

                            nombre = partes[0].split(
                                ". ",
                                1
                            )[1].strip()

                            fecha_original = partes[1].strip()

                            fecha_normalizada, fecha_obj = (
                                normalizar_fecha(
                                    fecha_original
                                )
                            )

                            # fecha invalida
                            if fecha_obj is None:

                                print(
                                    f"Fecha invalida: {nombre}"
                                )

                                continue

                            edad = calcular_edad(
                                fecha_obj
                            )

                            cumple = es_cumple(
                                fecha_obj
                            )

                            # =================================
                            # INSERT MYSQL
                            # =================================

                            cursor.execute("""
                            INSERT IGNORE INTO PERSONAS
                            (
                                nombre,
                                fecha_original,
                                fecha_normalizada,
                                edad,
                                cumple_hoy
                            )
                            VALUES (%s, %s, %s, %s, %s)
                            """, (
                                nombre,
                                fecha_original,
                                fecha_normalizada,
                                edad,
                                cumple
                            ))

                            # =================================
                            # CSV
                            # =================================

                            writer.writerow([
                                nombre,
                                fecha_original,
                                fecha_normalizada,
                                edad,
                                cumple
                            ])

                            insertados += 1

                        except Exception as e:

                            print(
                                "ERROR PERSONA:",
                                e
                            )

                            duplicados += 1

                # =============================================
                # MOSTRAR DATOS
                # =============================================

                cursor.execute("""
                SELECT *
                FROM PERSONAS
                """)

                datos = cursor.fetchall()

                encabezados = [
                    "ID",
                    "Nombre",
                    "Fecha Original",
                    "Fecha Normalizada",
                    "Edad",
                    "Cumple Hoy"
                ]

                mensaje = f"""
                Archivo de personas procesado correctamente.

                Insertados: {insertados}

                Duplicados/Error: {duplicados}
                """

            # =================================================
            # GUARDAR MYSQL
            # =================================================

            connection.commit()

            # =================================================
            # LOG
            # =================================================

            with open(
                "etl_log.txt",
                "a",
                encoding="utf-8"
            ) as log:

                log.write("\n")

                log.write("=" * 50 + "\n")

                log.write("REGISTRO ETL\n")

                log.write("=" * 50 + "\n")

                log.write(
                    f"Fecha: {datetime.now()}\n"
                )

                log.write(
                    f"Archivo: {archivo.filename}\n"
                )

                log.write(
                    f"Insertados: {insertados}\n"
                )

                log.write(
                    f"Duplicados/Error: {duplicados}\n"
                )

            # =================================================
            # CERRAR
            # =================================================

            connection.commit()

        except Exception as e:

            mensaje = f"Error: {str(e)}"

            print("ERROR GENERAL:", e)

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template(
        "index.html",
        mensaje=mensaje,
        datos=datos,
        encabezados=encabezados
    )


# =====================================================
# DESCARGAR LOG
# =====================================================

@app.route("/descargar-log")
def descargar_log():

    return send_file(
        "etl_log.txt",
        as_attachment=True
    )


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )