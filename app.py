from flask import Flask, render_template, request
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


@app.route("/", methods=["GET", "POST"])
def index():

    mensaje = ""
    datos = []

    if request.method == "POST":

        try:

            archivo = request.files["archivo"]

            # intentar utf-8 primero
            try:
                contenido = archivo.read().decode("utf-8")

            except:
                archivo.seek(0)
                contenido = archivo.read().decode("latin-1")

            lineas = contenido.splitlines()

            # limitar cantidad para no sobrecargar
            lineas = lineas[:100]

            # nueva conexion mysql
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

                # Guardar en archivo log
                with open("etl_log.txt", "a", encoding="utf-8") as log:
                    log.write(
                        f"{datetime.now()} | "
                        f"{original} -> {normalizado}\n"
                    )


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

            connection.commit()

            # obtener datos
            cursor.execute("""
            SELECT nombre_original, nombre_normalizado
            FROM COMUNAS_NORM
            LIMIT 100
            """)

            datos = cursor.fetchall()

            mensaje = f"""
            Proceso terminado.
            Insertados: {insertados}
            Duplicados eliminados: {duplicados}
            """

            # cerrar conexion
            cursor.close()
            connection.close()

        except Exception as e:

            mensaje = f"Error: {str(e)}"
            print("ERROR GENERAL:", e)

    return render_template(
        "index.html",
        mensaje=mensaje,
        datos=datos
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)