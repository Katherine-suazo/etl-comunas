from flask import Flask, render_template, request
import pymysql
from unidecode import unidecode
from datetime import datetime
from dotenv import load_dotenv
import os

# cargar variables .env
load_dotenv()

print("HOST:", os.getenv("MYSQLHOST"))
print("PORT:", os.getenv("MYSQLPORT"))
print("USER:", os.getenv("MYSQLUSER"))
print("DB:", os.getenv("MYSQLDATABASE"))

app = Flask(__name__)

# conexion mysql
connection = pymysql.connect(
    host=os.getenv("MYSQLHOST"),
    user=os.getenv("MYSQLUSER"),
    password=os.getenv("MYSQLPASSWORD"),
    database=os.getenv("MYSQLDATABASE"),
    port=int(os.getenv("MYSQLPORT"))
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
        archivo = request.files["archivo"]
        contenido = archivo.read().decode("utf-8")
        lineas = contenido.splitlines()

        # procesar maximo 100 registros
        lineas = lineas[:100]

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

        # limpiar tablas para pruebas
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

                print("ERROR:", e)

                duplicados += 1

        connection.commit()

        # obtener datos
        cursor.execute("""
        SELECT nombre_original, nombre_normalizado
        FROM COMUNAS_NORM
        LIMIT 20
        """)

        datos = cursor.fetchall()

        mensaje = f"""
        Proceso terminado.
        Insertados: {insertados}
        Duplicados eliminados: {duplicados}
        """

    return render_template(
        "index.html",
        mensaje=mensaje,
        datos=datos
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)