from datetime import datetime


def escribir_log_personas(nombre_archivo, total_original, procesados, insertados, duplicados, datos):
    with open("outputs/etl_log.txt", "w", encoding="utf-8") as log:
        log.write("\n")
        log.write("REGISTRO ETL\n")
        log.write("\n")
        log.write(f"Fecha: {datetime.now()}\n")
        log.write(f"Archivo: {nombre_archivo}\n")
        log.write(f"Registros archivo: {total_original}\n")
        log.write(f"Procesados: {procesados}\n")
        log.write(f"Insertados: {insertados}\n")
        log.write(f"Duplicados: {duplicados}\n")
        log.write("\n")

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
            log.write("-" * 80)
            log.write("\n")

            for fila in datos:
                log.write(
                    f"{fila[0]:<5}"
                    f"{fila[1]:<30}"
                    f"{fila[3]:<15}"
                    f"{fila[4]:<10}"
                    f"{fila[5]}\n"
                )

            log.write("\n")



def escribir_log_lugares(nombre_archivo,total_original,procesados,insertados,duplicados,lugares,direcciones,geos):
    with open("outputs/etl_log.txt", "w", encoding="utf-8") as log:
        log.write("\n")
        log.write("REGISTRO ETL\n")
        log.write("\n")
        log.write(f"Fecha: {datetime.now()}\n")
        log.write(f"Archivo: {nombre_archivo}\n")
        log.write(f"Registros archivo: {total_original}\n")
        log.write(f"Procesados: {procesados}\n")
        log.write(f"Insertados: {insertados}\n")
        log.write(f"Duplicados: {duplicados}\n")
        log.write("\n")

        # TABLA LUGARES
        if lugares:
            log.write("\n")
            log.write("TABLA LUGARES\n")
            log.write("\n")
            log.write(
                f"{'ID':<5}"
                f"{'LUGAR'}\n"
            )
            log.write("-" * 50)
            log.write("\n")

            for fila in lugares:
                log.write(
                    f"{fila[0]:<5}"
                    f"{fila[1]}\n"
                )

            log.write("\n")


        # TABLA DIRECCIONES
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
            log.write("-" * 120)
            log.write("\n")

            for fila in direcciones:
                log.write(
                    f"{fila[0]:<5}"
                    f"{str(fila[1]):<30}"
                    f"{str(fila[2]):<10}"
                    f"{str(fila[3]):<35}"
                    f"{str(fila[4])}\n"
                )

            log.write("\n")

        # TABLA GEOREFERENCIAS
        if geos:
            log.write("\n")
            log.write("TABLA GEOREFERENCIAS\n")
            log.write("\n")
            log.write(
                f"{'ID':<5}"
                f"{'LATITUD':<20}"
                f"{'LONGITUD'}\n"
            )
            log.write("-" * 60)
            log.write("\n")

            for fila in geos:
                log.write(
                    f"{fila[0]:<5}"
                    f"{str(fila[1]):<20}"
                    f"{str(fila[2])}\n"
                )

            log.write("\n")

        


def escribir_log_comunas(termino_busqueda, leidos, procesados, insertados, duplicados, no_encontrados, errores, comunas_guardadas):
    with open("outputs/log_comunas.txt", "w", encoding="utf-8") as log:
        log.write("REGISTRO ETL COMUNAS\n")
        log.write("=" * 80 + "\n\n")
        log.write(f"Fecha: {datetime.now()}\n")
        log.write(f"Búsqueda: {termino_busqueda}\n")
        log.write(f"Registros leídos: {leidos}\n")
        log.write(f"Comunas procesadas: {procesados}\n")
        log.write(f"Duplicados eliminados: {duplicados}\n")
        log.write(f"Consolidadas correctamente: {insertados}\n")
        log.write(f"No encontradas: {no_encontrados}\n")
        log.write(f"Errores: {errores}\n")
        log.write("\n")
        log.write("=" * 80)
        log.write("\n\n")

        if comunas_guardadas:
            log.write("COMUNAS CONSOLIDADAS\n")
            log.write("\n")
            log.write(
                f"{'ID':<5}"
                f"{'COMUNA':<30}"
                f"{'REGION':<25}"
                f"{'PROVINCIA':<25}"
                f"{'HABITANTES'}\n"
            )
            log.write("-" * 120)
            log.write("\n")

            for fila in comunas_guardadas:
                log.write(
                    f"{fila[0]:<5}"
                    f"{str(fila[1]):<30}"
                    f"{str(fila[2]):<25}"
                    f"{str(fila[3]):<25}"
                    f"{str(fila[4])}\n"
                )