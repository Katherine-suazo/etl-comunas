from flask import Flask, render_template, request, send_file
import pymysql
from unidecode import unidecode
from datetime import datetime
from dotenv import load_dotenv
import os
import csv
import re

load_dotenv()

app = Flask(__name__)

# conexion mysql
def conectar_db():
    return pymysql.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT")),
        connect_timeout=10,
        autocommit=True
    )

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

    return (
        fecha.day == hoy.day and
        fecha.month == hoy.month
    )

@app.route("/", methods=["GET", "POST"])
def index():

    mensaje = ""
    datos = []
    encabezados = []
    lugares = []
    direcciones = []
    geos = []

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
                    encabezados=encabezados,
                    lugares=lugares,
                    direcciones=direcciones,
                    geos=geos
                )

            # leer archivo
            try:
                contenido = archivo.read().decode("utf-8")
            except:
                archivo.seek(0)
                contenido = archivo.read().decode("latin-1")

            lineas_completas = contenido.splitlines()
            total_original = len(lineas_completas)

            # maximo 100 lineas
            lineas = lineas_completas[:100]

            # mysql
            connection = conectar_db()
            cursor = connection.cursor()

            # tablas
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
                pais VARCHAR(255),
                UNIQUE(
                    nombre_calle,
                    numero_calle,
                    ciudad_estado_provincia,
                    pais
                )
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS GEOREFERENCIAS (
                id INT AUTO_INCREMENT PRIMARY KEY,
                latitud VARCHAR(50),
                longitud VARCHAR(50),
                UNIQUE(latitud, longitud)
            )
            """)

            # limpiar tablas
            cursor.execute("DELETE FROM PERSONAS")
            cursor.execute("DELETE FROM LUGARES")
            cursor.execute("DELETE FROM DIRECCIONES")
            cursor.execute("DELETE FROM GEOREFERENCIAS")

            insertados = 0
            duplicados = 0

            # ============================================
            # ARCHIVO LUGARES
            # ============================================

            if ";" in contenido:
                csv_nombre = "lugares_limpio.csv"

                with open(csv_nombre, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([
                        "Lugar",
                        "Nombre Calle",
                        "Numero Calle",
                        "Ciudad Estado Provincia",
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
                                duplicados += 1
                                continue

                            lugar = normalizar_texto(partes[0])
                            direccion = partes[1].strip()
                            geo = partes[2].strip()

                            # geo
                            if "," not in geo:
                                duplicados += 1
                                continue

                            geo_partes = geo.split(",")

                            if len(geo_partes) < 2:
                                duplicados += 1
                                continue

                            latitud = geo_partes[0].strip()
                            longitud = geo_partes[1].strip()

                            # direccion
                            direccion_partes = [x.strip() for x in direccion.split(",")]

                            nombre_calle = ""
                            numero = ""
                            ciudad_estado = ""
                            pais = ""

                            if len(direccion_partes) == 1:
                                nombre_calle = direccion_partes[0]

                            elif len(direccion_partes) >= 2:
                                pais = direccion_partes[-1]
                                primer_parte = direccion_partes[0]
                                match = re.match(r"^(\d+)\s+(.*)", primer_parte)

                                if match:
                                    numero = match.group(1)
                                    nombre_calle = match.group(2)

                                else:
                                    nombre_calle = primer_parte

                                if len(direccion_partes) > 2:
                                    ciudad_estado = ", ".join(direccion_partes[1:-1])

                            # insertar lugar
                            try:
                                cursor.execute("""
                                INSERT INTO LUGARES (nombre)
                                VALUES (%s)
                                """, (lugar,))

                                insertados += 1

                            except:
                                duplicados += 1
                                continue

                            # insertar direccion
                            try:
                                cursor.execute("""
                                INSERT IGNORE INTO DIRECCIONES
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

                            except Exception as e:
                                print("ERROR DIRECCION:", e)

                            # insertar geo
                            try:
                                cursor.execute("""
                                INSERT IGNORE INTO GEOREFERENCIAS
                                (
                                    latitud,
                                    longitud
                                )
                                VALUES (%s, %s)
                                """, (
                                    latitud,
                                    longitud
                                ))

                            except Exception as e:
                                print("ERROR GEO:", e)

                            # csv limpio
                            writer.writerow([
                                lugar,
                                nombre_calle,
                                numero,
                                ciudad_estado,
                                pais,
                                latitud,
                                longitud
                            ])

                        except Exception as e:
                            print("ERROR GENERAL LUGAR:", e)
                            duplicados += 1

                # mostrar tablas
                cursor.execute("SELECT * FROM LUGARES")
                lugares = cursor.fetchall()

                cursor.execute("SELECT * FROM DIRECCIONES")
                direcciones = cursor.fetchall()

                cursor.execute("SELECT * FROM GEOREFERENCIAS")
                geos = cursor.fetchall()

                mensaje = f"""
                Proceso terminado.

                - Total registros archivo: {total_original}
                - Registros procesados: {len(lineas)}
                - Duplicados eliminados: {duplicados}
                - Insertados: {insertados}
                """

            # ============================================
            # ARCHIVO PERSONAS
            # ============================================

            else:
                csv_nombre = "personas_limpio.csv"

                with open(csv_nombre, "w", newline="", encoding="utf-8") as csvfile:
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
                            nombre = partes[0].split(". ", 1)[1].strip()
                            fecha_original = partes[1].strip()
                            fecha_normalizada, fecha_obj = normalizar_fecha(fecha_original)

                            if fecha_obj is None:
                                duplicados += 1
                                continue

                            edad = calcular_edad(fecha_obj)
                            cumple = es_cumple(fecha_obj)

                            try:
                                cursor.execute("""
                                INSERT INTO PERSONAS
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

                                insertados += 1

                            except:
                                duplicados += 1
                                continue

                            writer.writerow([
                                nombre,
                                fecha_original,
                                fecha_normalizada,
                                edad,
                                cumple
                            ])

                        except Exception as e:
                            print("ERROR PERSONA:", e)
                            duplicados += 1

                cursor.execute("SELECT * FROM PERSONAS")
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
                Proceso terminado.
                - Total registros archivo: {total_original}
                - Registros procesados: {len(lineas)}
                - Duplicados eliminados: {duplicados}
                - Insertados: {insertados}
                """

            # ============================================
            # LOG
            # ============================================

            with open("etl_log.txt", "w", encoding="utf-8") as log:

                log.write("\n")
                log.write("REGISTRO ETL\n")
                log.write(f"Fecha: {datetime.now()}\n")
                log.write(f"Archivo: {archivo.filename}\n")
                log.write(f"Registros archivo: {total_original}\n")
                log.write(f"Procesados: {len(lineas)}\n")
                log.write(f"Insertados: {insertados}\n")
                log.write(f"Duplicados: {duplicados}\n")
                log.write("\n")

                # ========================================
                # PERSONAS
                # ========================================

                if datos:

                    log.write("\n")
                    log.write("TABLA PERSONAS\n")
                    log.write("\n")

                    log.write(
                        f"{'ID':<5}"
                        f"{'NOMBRE':<30}"
                        f"{'FECHA':<15}"
                        f"{'EDAD':<10}"
                        f"{'CUMPLE'}\n"
                    )

                    for fila in datos:

                        log.write(
                            f"{fila[0]:<5}"
                            f"{fila[1]:<30}"
                            f"{fila[3]:<15}"
                            f"{fila[4]:<10}"
                            f"{fila[5]}\n"
                        )

                    log.write("\n")

                # ========================================
                # LUGARES
                # ========================================

                if lugares:

                    log.write("\n")
                    log.write("TABLA LUGARES\n")
                    log.write("\n")

                    log.write(
                        f"{'ID':<5}"
                        f"{'LUGAR'}\n"
                    )

                    for fila in lugares:

                        log.write(
                            f"{fila[0]:<5}"
                            f"{fila[1]}\n"
                        )

                    log.write("\n")

                # ========================================
                # DIRECCIONES
                # ========================================

                if direcciones:

                    log.write("\n")
                    log.write("TABLA DIRECCIONES\n")
                    log.write("\n")

                    log.write(
                        f"{'ID':<5}"
                        f"{'CALLE':<30}"
                        f"{'NUM':<10}"
                        f"{'CIUDAD/ESTADO':<35}"
                        f"{'PAIS'}\n"
                    )

                    for fila in direcciones:

                        log.write(
                            f"{fila[0]:<5}"
                            f"{str(fila[1]):<30}"
                            f"{str(fila[2]):<10}"
                            f"{str(fila[3]):<35}"
                            f"{str(fila[4])}\n"
                        )

                    log.write("\n")

                # ========================================
                # GEOREFERENCIAS
                # ========================================

                if geos:

                    log.write("\n")
                    log.write("TABLA GEOREFERENCIAS\n")
                    log.write("\n")

                    log.write(
                        f"{'ID':<5}"
                        f"{'LATITUD':<20}"
                        f"{'LONGITUD'}\n"
                    )

                    for fila in geos:

                        log.write(
                            f"{fila[0]:<5}"
                            f"{str(fila[1]):<20}"
                            f"{str(fila[2])}\n"
                        )

                    log.write("\n")

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
        encabezados=encabezados,
        lugares=lugares,
        direcciones=direcciones,
        geos=geos
    )

# descargar log
@app.route("/descargar-log")
def descargar_log():
    return send_file(
        "etl_log.txt",
        as_attachment=True
    )

# main
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )