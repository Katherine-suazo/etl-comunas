from database.conexion import conectar_db
from services.normalizador import (normalizar_texto, descomponer_direccion)
from services.log_service import escribir_log_lugares
import csv


def crear_tablas_lugares(cursor):

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


def limpiar_tablas_lugares(cursor):
    cursor.execute("TRUNCATE TABLE LUGARES")
    cursor.execute("TRUNCATE TABLE DIRECCIONES")
    cursor.execute("TRUNCATE TABLE GEOREFERENCIAS")


def construir_clave_fila_lugar(lugar, direccion, latitud, longitud):
    return (
        normalizar_texto(lugar).lower(),
        normalizar_texto(direccion).lower(),
        latitud.strip(),
        longitud.strip()
    )


def procesar_lugares(contenido, nombre_archivo):
    connection = None
    cursor = None
    lugares = []
    direcciones = []
    geos = []

    try:
        lineas_completas = contenido.splitlines()
        total_original = len(lineas_completas)

        # máximo 100 líneas
        lineas = lineas_completas[:100]

        connection = conectar_db()
        cursor = connection.cursor()

        crear_tablas_lugares(cursor)
        limpiar_tablas_lugares(cursor)

        insertados = 0
        duplicados = 0

        filas_vistas = set()
        csv_nombre = "outputs/lugares_limpio.csv"

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

                    # validar georreferencia
                    if "," not in geo:
                        duplicados += 1
                        continue

                    geo_partes = geo.split(",")

                    if len(geo_partes) < 2:
                        duplicados += 1
                        continue

                    latitud = geo_partes[0].strip()
                    longitud = geo_partes[1].strip()

                    clave_fila = construir_clave_fila_lugar(lugar, direccion, latitud, longitud)

                    if clave_fila in filas_vistas:
                        duplicados += 1
                        continue

                    filas_vistas.add(clave_fila)

                    # procesar dirección
                    (nombre_calle, numero, ciudad_estado, pais) = descomponer_direccion(direccion)

                    # insertar lugar
                    try:
                        cursor.execute("""
                        INSERT IGNORE INTO LUGARES (nombre)
                        VALUES (%s)
                        """, (lugar,))

                        insertados += 1

                    except Exception as e:
                        print("ERROR LUGAR:", e)

                    # insertar dirección
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

                    # insertar georreferencia
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

                    # guardar csv limpio
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

        # log
        escribir_log_lugares(
            nombre_archivo,
            total_original,
            len(lineas),
            insertados,
            duplicados,
            lugares,
            direcciones,
            geos
        )

        return {
            "mensaje": mensaje,
            "lugares": lugares,
            "direcciones": direcciones,
            "geos": geos
        }

    except Exception as e:
        print("ERROR LUGARES:", e)
        return {
            "mensaje": f"Error: {str(e)}",
            "lugares": [],
            "direcciones": [],
            "geos": []
        }

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()