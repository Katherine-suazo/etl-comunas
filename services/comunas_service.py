from database.conexion import conectar_db
from services.api_service import (buscar_comuna_api)


def crear_tabla_comunas(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS COMUNAS (
        id INT AUTO_INCREMENT PRIMARY KEY,
        comuna VARCHAR(255) UNIQUE,
        region VARCHAR(255),
        provincia VARCHAR(255),
        habitantes INT
    )
    """)


def guardar_comuna(cursor, comuna):
    try:
        cursor.execute("""
        INSERT INTO COMUNAS
        (
            comuna,
            region,
            provincia,
            habitantes
        )
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            region = VALUES(region),
            provincia = VALUES(provincia),
            habitantes = VALUES(habitantes)
        """, (
            comuna["comuna"],
            comuna["region"],
            comuna["provincia"],
            comuna["habitantes"]
        ))
        return True

    except Exception as e:
        print("ERROR GUARDAR COMUNA:", e)
        return False


def buscar_y_guardar_comuna(nombre_comuna):
    connection = None
    cursor = None

    try:
        connection = conectar_db()
        cursor = connection.cursor()
        crear_tabla_comunas(cursor)
        resultados_api = buscar_comuna_api(nombre_comuna)

        if not resultados_api:
            return {
                "success": False,
                "mensaje": "No se encontraron comunas.",
                "comunas": []
            }

        insertados = 0

        for comuna in resultados_api:
            guardado = guardar_comuna(cursor, comuna)

            if guardado:
                insertados += 1

        # obtener comunas guardadas
        cursor.execute("""
        SELECT
            id,
            comuna,
            region,
            provincia,
            habitantes
        FROM COMUNAS
        ORDER BY comuna
        """)

        comunas_guardadas = cursor.fetchall()

        mensaje = f"""
        Proceso completado.
        - Comunas encontradas API: {len(resultados_api)}
        - Comunas guardadas/actualizadas: {insertados}
        """

        return {
            "success": True,
            "mensaje": mensaje,
            "comunas": comunas_guardadas
        }

    except Exception as e:
        print("ERROR COMUNAS SERVICE:", e)
        return {
            "success": False,
            "mensaje": f"Error: {str(e)}",
            "comunas": []
        }

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def obtener_comunas():
    connection = None
    cursor = None
    try:
        connection = conectar_db()
        cursor = connection.cursor()
        crear_tabla_comunas(cursor)
        cursor.execute("""
        SELECT
            id,
            comuna,
            region,
            provincia,
            habitantes
        FROM COMUNAS
        ORDER BY comuna
        """)

        comunas = cursor.fetchall()
        return comunas

    except Exception as e:
        print("ERROR OBTENER COMUNAS:", e)
        return []

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()