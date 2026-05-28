from database.conexion import conectar_db
from services.normalizador import (separar_persona_y_fecha, normalizar_fecha, calcular_edad, es_cumple)
from services.log_service import escribir_log_personas
import csv


def crear_tabla_personas(cursor):
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


def limpiar_tabla_personas(cursor):
    cursor.execute("TRUNCATE TABLE PERSONAS")


def procesar_personas(contenido, nombre_archivo):
    connection = None
    cursor = None
    datos = []
    encabezados = []

    try:

        lineas_completas = contenido.splitlines()
        total_original = len(lineas_completas)

        # máximo 100 líneas
        lineas = lineas_completas[:100]

        connection = conectar_db()
        cursor = connection.cursor()

        crear_tabla_personas(cursor)
        limpiar_tabla_personas(cursor)

        insertados = 0
        duplicados = 0

        csv_nombre = "outputs/personas_limpio.csv"

        with open(csv_nombre, "w", newline="", encoding="utf-8") as csvfile:

            writer = csv.writer(csvfile)
            writer.writerow(["Nombre", "Fecha Original", "Fecha Normalizada", "Edad", "Cumple Hoy"])

            for linea in lineas:

                if linea.strip() == "":
                    continue

                try:
                    nombre, fecha_original = separar_persona_y_fecha(linea)

                    if not nombre or not fecha_original:
                        duplicados += 1
                        continue

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

                    writer.writerow([nombre, fecha_original, fecha_normalizada, edad, cumple ])

                except Exception as e:
                    print("ERROR PERSONA:", e)

                    duplicados += 1

        # obtener datos para mostrar
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

        # log
        escribir_log_personas(
            nombre_archivo,
            total_original,
            len(lineas),
            insertados,
            duplicados,
            datos
        )

        return {
            "mensaje": mensaje,
            "datos": datos,
            "encabezados": encabezados
        }

    except Exception as e:
        print("ERROR PERSONAS:", e)
        return {
            "mensaje": f"Error: {str(e)}",
            "datos": [],
            "encabezados": []
        }

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()