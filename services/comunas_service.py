from database.conexion import conectar_db
from services.api_service import buscar_comuna_api
from services.log_service import escribir_log_comunas


def crear_tabla_comunas(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS COMUNAS (
        id INT AUTO_INCREMENT PRIMARY KEY,
        comuna VARCHAR(255),
        comuna_normalizada VARCHAR(255) UNIQUE,
        region VARCHAR(255),
        provincia VARCHAR(255),
        habitantes INT
    )
    """)


def guardar_comuna(cursor, comuna):
    try:
        cursor.execute("""
        INSERT INTO COMUNAS (comuna, comuna_normalizada, region, provincia, habitantes)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            comuna = VALUES(comuna),
            region = VALUES(region),
            provincia = VALUES(provincia),
            habitantes = VALUES(habitantes)

        """, (
            comuna["comuna"],
            comuna["comuna_normalizada"],
            comuna["region"],
            comuna["provincia"],
            comuna["habitantes"]
        ))

        return True

    except Exception as e:
        print("ERROR GUARDAR COMUNA:", e)
        return False


def buscar_y_guardar_comuna(nombre_comuna, formato):
    connection = None
    cursor = None

    try:
        connection = conectar_db()
        cursor = connection.cursor()
        #cursor.execute("DROP TABLE IF EXISTS COMUNAS")
        crear_tabla_comunas(cursor)
        resultados_api = buscar_comuna_api(nombre_comuna, formato)

        if not resultados_api:
            escribir_log_comunas(nombre_comuna, 1, 0, 0, 0, 1, 0, [])
            #sugerencias = obtener_sugerencias(nombre_comuna)
            return {"success": False, "mensaje": "No se encontraron comunas.", "comunas": []}

        insertados = 0
        duplicados = 0
        errores = 0

        comunas_vistas = set()

        for comuna in resultados_api:
            nombre_normalizado = comuna["comuna_normalizada"]

            # eliminar duplicados en memoria
            if nombre_normalizado in comunas_vistas:
                duplicados += 1
                continue

            comunas_vistas.add(nombre_normalizado)
            guardado = guardar_comuna(cursor, comuna)

            if guardado:
                insertados += 1
            else:
                errores += 1

        cursor.execute("SELECT id, comuna, region, provincia,habitantes FROM COMUNAS ORDER BY comuna")
        comunas_guardadas = cursor.fetchall()

        escribir_log_comunas(
            nombre_comuna,
            1,
            len(resultados_api),
            insertados,
            duplicados,
            0,
            errores,
            comunas_guardadas
        )

        mensaje = f"""
        Proceso completado.
        Comunas encontradas API: {len(resultados_api)}
        Procesadas: {len(resultados_api)}
        Duplicados eliminados: {duplicados}
        Guardadas/Actualizadas: {insertados}
        Errores: {errores}
        """

        return {"success": True, "mensaje": mensaje, "comunas": comunas_guardadas}

    except Exception as e:
        print("ERROR COMUNAS:", e)
        return {"success": False, "mensaje": f"Error: {str(e)}", "comunas": []}

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
        cursor.execute("SELECT id, comuna, region, provincia, habitantes FROM COMUNAS ORDER BY comuna")
        return cursor.fetchall()

    except Exception as e:
        print("ERROR OBTENER COMUNAS:",e)
        return []

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


#def obtener_sugerencias(nombre_busqueda):
    #connection = conectar_db()
    #cursor = connection.cursor()
    #cursor.execute("SELECT comuna FROM COMUNAS WHERE comuna LIKE %s LIMIT 5", (f"%{nombre_busqueda}%",))
    #sugerencias = [fila[0] for fila in cursor.fetchall()]
    #cursor.close()
    #connection.close()
    #return sugerencias




    