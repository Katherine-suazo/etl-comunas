from flask import Flask, render_template, request, send_file
from services.personas_service import procesar_personas
from services.lugares_service import procesar_lugares
from services.comunas_service import buscar_y_guardar_comuna, obtener_comunas


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
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
                return render_template("index.html", mensaje=mensaje)

            archivo = request.files["archivo"]

            if archivo.filename == "":
                mensaje = "No se ha seleccionado ningún archivo."
                return render_template("index.html", mensaje=mensaje)

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
        "index.html",
        mensaje=mensaje,
        datos=datos,
        encabezados=encabezados,
        lugares=lugares,
        direcciones=direcciones,
        geos=geos
    )


@app.route("/descargar-log")
def descargar_log():
    return send_file("outputs/log.txt", as_attachment=True)
            

@app.route("/comunas", methods=["GET", "POST"])
def comunas():
    mensaje = ""
    comunas = []

    if request.method == "POST":
        nombre_comuna = request.form.get("comuna")
        formato = request.form.get("formato")
        resultado = buscar_y_guardar_comuna(nombre_comuna, formato)
        mensaje = resultado["mensaje"]
        comunas = resultado["comunas"]

    return render_template("comunas.html", mensaje=mensaje, comunas=comunas)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
