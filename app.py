# cd entorno cd scripts activate.bat
# pyhton -m venv entorno
from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
cadenaConexion = "mysql+pymysql://root@localhost/tiendaorm"
#Cadena de conexion a la base de datos 
app.config['SQLALCHEMY_DATABASE_URI'] = cadenaConexion
app.config["UPLOAD_FOLDER"]="./static/imagenes"
#Objeto que representa la base de datos
db = SQLAlchemy(app)
@app.route("/")
def inicio():
    return render_template("Inicio.html")


from controller.controllerProducto import*
from controller.controllerCategoria import*

#Crea las tablas en la base de datos sino existen,se crean de acuerdo al modelo
with app.app_context():
    db.create_all()

if __name__ =="__main__":
    app.run(port=5000,debug=True)