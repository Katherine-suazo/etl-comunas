from flask import Flask, render_template, request, send_file
import pymysql
from unidecode import unidecode
from datetime import datetime
from dotenv import load_dotenv
import os

# cargar variables .env
load_dotenv()

app = Flask(__name__)


# funcion conexion mysql
def conectar_db():

    return pymysql.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT")),
        connect_timeout=10
    )


# funcion normalizar
def normalizar(texto):

    original = texto.strip()

    texto = original.upper()
    texto = unidecode(texto)
    texto = " ".join(texto.split())

    return original, texto


# ruta principal
@app.route("/", methods=["GET", "POST"])
def index():

    mensaje = ""
    datos = []

    if request.method == "POST":

        connection = None
        cursor = None

        try:

            archivo = request.files["archivo"]

            # validar archivo
            if archivo.filename == "":
                mensaje = "Debe seleccionar un archivo."

                return render_template(
                    "index.html",
                    mensaje=mensaje,
                    datos=datos
                )

            # intentar UTF-8 primero
            try:

                contenido = archivo.read().decode("utf-8")

            except:

                archivo.seek(0)
                contenido = archivo.read().decode("latin-1")

            # obtener lineas
            lineas_completas = contenido.splitlines()

            total_original = len(lineas_completas)

            # limitar procesamiento
            lineas = lineas_completas[:100]

            # conexion mysql
            connection = conectar_db()
            cursor = connection.cursor()

            # crear tablas
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS COMUNAS_NORM (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre_original VARCHAR(255),
                nombre_normalizado VARCHAR(255) UNIQUE
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS LOG_CAMBIOS (
                id INT AUTO_INCREMENT PRIMARY KEY,
                original_texto VARCHAR(255),
                nuevo_texto VARCHAR(255),
                fecha DATETIME
            )
            """)

            # limpiar tablas
            cursor.execute("DELETE FROM COMUNAS_NORM")
            cursor.execute("DELETE FROM LOG_CAMBIOS")

            insertados = 0
            duplicados = 0

            for linea in lineas:

                if linea.strip() == "":
                    continue

                original, normalizado = normalizar(linea)

                try:

                    cursor.execute("""
                    INSERT INTO COMUNAS_NORM
                    (nombre_original, nombre_normalizado)
                    VALUES (%s, %s)
                    """, (original, normalizado))

                    cursor.execute("""
                    INSERT INTO LOG_CAMBIOS
                    (original_texto, nuevo_texto, fecha)
                    VALUES (%s, %s, %s)
                    """, (
                        original,
                        normalizado,
                        datetime.now()
                    ))

                    insertados += 1

                except Exception as e:

                    print("DUPLICADO:", e)
                    duplicados += 1

            # guardar cambios
            connection.commit()

            # obtener datos insertados
            cursor.execute("""
            SELECT nombre_original, nombre_normalizado
            FROM COMUNAS_NORM
            """)

            datos = cursor.fetchall()

            # crear log NUEVO (borra el anterior)
            with open("etl_log.txt", "w", encoding="utf-8") as log:

                log.write("\n")
                log.write("=" * 50 + "\n")
                log.write("REGISTRO ETL\n")
                log.write("=" * 50 + "\n\n")

                log.write(f"Fecha: {datetime.now()}\n")
                log.write(f"Archivo: {archivo.filename}\n")
                log.write(f"Registros archivo: {total_original}\n")
                log.write(f"Registros procesados: {len(lineas)}\n")
                log.write(f"Insertados: {insertados}\n")
                log.write(f"Duplicados eliminados: {duplicados}\n\n")

                log.write("- Archivo leído correctamente\n")
                log.write("- Limpieza aplicada\n")
                log.write("- Normalización completada\n")
                log.write("- Datos guardados en MySQL\n")

            mensaje = f"""
            Proceso terminado.

            - Total registros archivo: {total_original}

            - Registros procesados: {len(lineas)}

            - Insertados: {insertados}

            - Duplicados eliminados: {duplicados}
            """

        except Exception as e:

            mensaje = f"Error: {str(e)}"
            print("ERROR GENERAL:", e)

        finally:

            # cerrar conexion
            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template(
        "index.html",
        mensaje=mensaje,
        datos=datos
    )


# descargar log
@app.route("/descargar-log")
def descargar_log():

    return send_file(
        "etl_log.txt",
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)