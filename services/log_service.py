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

        # ========================================
        # TABLA PERSONAS
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