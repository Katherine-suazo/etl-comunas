from flask import Flask, render_template, request, send_file
from database.conexion import conectar_db
from services.personas_service import procesar_personas
from services.lugares_service import procesar_lugares
from services.famosos_service import obtener_info_famoso
from services.comunas_service import buscar_y_guardar_comuna
from os.path import exists


app = Flask(__name__)



@app.route("/")
def inicio():
    return render_template("index.html")



@app.route("/procesar", methods=["GET", "POST"])
def index():
    mensaje = ""
    datos = []
    encabezados = []
    lugares = []
    direcciones = []
    geos = []

    if request.method == "POST":
        try:
            # validar archivo
            if "archivo" not in request.files:
                mensaje = "Debe seleccionar un archivo."
                return render_template("procesar.html", mensaje=mensaje)

            archivo = request.files["archivo"]

            if archivo.filename == "":
                mensaje = "No se ha seleccionado ningún archivo."
                return render_template("procesar.html", mensaje=mensaje)

            # leer archivo
            try:
                contenido = archivo.read().decode("utf-8")

            except:
                archivo.seek(0)
                contenido = archivo.read().decode("latin-1")

            # detectar tipo de archivo
            if ";" in contenido:
                resultado = procesar_lugares(contenido, archivo.filename)
                mensaje = resultado["mensaje"]
                lugares = resultado["lugares"]
                direcciones = resultado["direcciones"]
                geos = resultado["geos"]

            else:
                resultado = procesar_personas(contenido, archivo.filename)
                mensaje = resultado["mensaje"]
                datos = resultado["datos"]
                encabezados = resultado["encabezados"]

        except Exception as e:
            mensaje = (f"Error al procesar el archivo: {str(e)}")
            print("ERROR APP:", e)

    return render_template(
        "procesar.html",
        mensaje=mensaje,
        datos=datos,
        encabezados=encabezados,
        lugares=lugares,
        direcciones=direcciones,
        geos=geos
    )


@app.route("/descargar-log")
def descargar_log():
    return send_file("outputs/etl_log.txt", as_attachment=True)
            

@app.route("/comunas", methods=["GET", "POST"])
def comunas():
    mensaje = ""
    comunas = []
    sugerencias = []

    if request.method == "POST":
        nombre_comuna = request.form.get("comuna")
        formato = request.form.get("formato")

        resultado = buscar_y_guardar_comuna(nombre_comuna, formato)

        mensaje = resultado["mensaje"]
        comunas = resultado["comunas"]
        sugerencias = resultado.get("sugerencias", [])

    return render_template("comunas.html", mensaje=mensaje, comunas=comunas, sugerencias=sugerencias)


@app.route("/descargar-log-comunas")
def descargar_log_comunas():
    return send_file("outputs/log_comunas.txt", as_attachment=True)


@app.route("/famoso/<path:nombre>")
def ver_famoso(nombre):
    famoso = obtener_info_famoso(nombre)
    return render_template("crearFamoso.html", famoso=famoso)


@app.route("/mapa")
def mapa():
    connection = conectar_db()
    cursor = connection.cursor()

    cursor.execute("SELECT latitud, longitud FROM GEOREFERENCIAS")
    lugares = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("mapa.html", lugares=lugares)



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
