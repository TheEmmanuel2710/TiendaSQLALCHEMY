from app import app,db
from model.categoria import *
from flask import Flask, render_template,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc


@app.route("/agregarCategoria", methods=["GET", "POST"])
def agregarCategorias():
    if request.method == "POST":
        try:
            nombre = request.form["txtNombre"]
            categoria = Categoria(catNombre=nombre)
            db.session.add(categoria)
            db.session.commit()
            mensaje = "Categoria agregada correctamente"
        except exc.SQLAlchemyError as error:
            db.session.rollback()
            mensaje = str(error)
        return render_template("frmAgregarCategoria.html", categoria=categoria, mensaje=mensaje)
    return render_template("frmAgregarCategoria.html")
