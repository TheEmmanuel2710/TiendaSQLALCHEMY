from app import app
from model.producto import *
from model.categoria import *
from flask import Flask, render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from werkzeug.utils import secure_filename
import os

@app.route("/listarProductos")
def listarProducto():
    try:
        listaProductos=Producto.query.all()
    except exc.SQLAlchemyError as error:
        mensaje=str(error)
    return render_template("listarProductos.html",listaProductos=listaProductos)

@app.route("/vistaProducto",methods=["GET"])
def vistaProducto():
    producto=None
    #Obtener las categorias que se muestran del formulario 
    listaCategorias=Categoria.query.all()
    return render_template("frmAgregarProducto.html",producto=producto,listaCategorias=listaCategorias)

@app.route("/agregarProducto", methods=["POST"])
def agregarProducto():
    mensaje = ""
    try:
        # Recibir los valores  de la vista en variables locales
        codigo = int(request.form["txtCodigo"])
        nombre = request.form["txtNombre"]
        precio = int(request.form["txtPrecio"])
        categoria = request.form["cbCategoria"]
        # creacion de objeto producto 
        producto =Producto(proCodigo=codigo,proNombre=nombre,proPrecio=precio,proCategoria=categoria)
        db.session.add(producto)
        db.session.commit()
        # Datos de la imagen
        archivo = request.files['fileFoto']
        nombreArchivo = secure_filename(archivo.filename)
        listaNombreArchivo = nombreArchivo.rsplit(".", 1)
        extension = listaNombreArchivo[1].lower()
        nuevoNombre = str(producto.idProducto)+"."+extension
        archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nuevoNombre))
        mensaje="Producto agregado correctamente"
        return redirect("/listarProductos")
    except exc.SQLAlchemyError as error:
        db.session.rollback()
        mensaje = str(error)
    return render_template("frmAgregarProducto.html", producto=producto, mensaje=mensaje)
    

@app.route("/consultarProducto/<string:idProducto>", methods=["GET"])
def consultarXid(idProducto):
    try:
        producto = Producto.query.get(idProducto)
        listaCategoria=Categoria.query.all()
    except  exc.SQLAlchemyError as error:
        mensaje =str(error) 
    return render_template("frmEditar.html", producto=producto,listaCategoria=listaCategoria)

@app.route("/actualizarProducto", methods=["POST"])
def actualizarProducto():
    try:
        idProducto = request.form["idProducto"]
        producto = Producto.query.get(idProducto)
        nuevo_codigo = int(request.form["txtCodigo"])
        
        # Validar si el nuevo código de producto ya existe en la base de datos
        if producto.proCodigo != nuevo_codigo and validar_producto_existente(nuevo_codigo):
            mensaje = "Error: El código {} ya está en uso.".format(nuevo_codigo)
            listaCategoria = Categoria.query.all()
            return render_template("frmEditar.html", producto=producto, listaCategoria=listaCategoria, mensaje=mensaje)
        else:
            producto.proCodigo = nuevo_codigo
            producto.proNombre = request.form["txtNombre"]
            producto.proPrecio = request.form["txtPrecio"]
            producto.proCategoria = request.form["cbCategoria"]
            db.session.commit()
            archivo = request.files['fileFoto']
            if archivo.filename != "":
                nombreArchivo = secure_filename(archivo.filename)
                listaNombreArchivo = nombreArchivo.rsplit(".", 1)
                extension = listaNombreArchivo[1].lower()
                nuevoNombre = str(producto.idProducto) + "." + extension
                archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nuevoNombre))
            return redirect("/listarProductos")
    except exc.SQLAlchemyError as error:
        mensaje = str(error)
        return render_template("frmEditar.html")
    
    
@app.route("/eliminar/<string:idProducto>",methods=["GET"])
def eliminar(idProducto):
    try:
        producto=Producto.query.get(idProducto)
        db.session.delete(producto)
        listaProductos=Producto.query.all()
        db.session.commit()
        nuevoArchivo=str(idProducto)+".jpg"
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"]+"/"+nuevoArchivo))
        mensaje="Producto eliminado"
    except  exc.SQLAlchemyError as error:
        db.session.rollback()
        mensaje = "Problemas al eliminar"
    listaProductos=Producto.query.all()
    return render_template("listarProductos.html",listaProductos=listaProductos,mensaje=mensaje)


def validar_producto_existente(codigo):
    """
    Función para validar si un producto con el mismo código ya existe en la base de datos.
    :param codigo: Código del producto a validar.
    :return: True si el producto ya existe, False si no.
    """
    producto_existente = Producto.query.filter_by(proCodigo=codigo).first()
    if producto_existente:
        return True
    else:
        return False

@app.route("/obtenerCategoriasJson",methods=["GET"])
def obtenerCategoriasJson():
    listaCategorias=Categoria.query.all()
    listJson=[]
    for categoria in listaCategorias:
        categoria={
            "idCategoria":categoria.idCategoria,
            "catNombre":categoria.catNombre 
        }
        listJson.append(categoria)
    return listJson

@app.route("/agregarCategoriaJson",methods=["POST"])
def agregarCategoriaJson():
    try:
        datos=request.get_json()
        categoria=Categoria(catNombre=datos["nombreCategoria"])
        db.session.add(categoria)
        db.session.commit()
        mensaje="Categoria agregada"
    except exc.SQLAlchemyError as error:
        db.session.rollback()
        mensaje="Problemas al agregar la categoria"
    return {"mensaje":mensaje}

@app.route("/listarProductoJson",methods=["GET"])
def listarProductoJson():
    try:
        listaProductos=Producto.query.all()
        listJson=[]
        for producto in listaProductos:
            producto={
                "idProducto":producto.idProducto,
                "proNombre":producto.proNombre, 
                "proPrecio":producto.proPrecio, 
                "categoria":{
                    "idCategoria":producto.categoria.idCategoria,
                    "catNombre":producto.categoria.catNombre 
                } 
            }
            listJson.append(producto)
        mensaje="Lista de productos"
    except exc.SQLAlchemyError as error:
        mensaje("Problemas al obtener los productos")
    return {"mensaje":mensaje,"listaProductos":listJson}

@app.route("/consultarProductoJson",methods=["GET"])
def consultarProductoJson():
    try:
        datos=request.get_json(force=True)
        idProducto=int(datos["idProducto"])
        producto=Producto.query.get(idProducto)
        productoJson={
            "idProducto":producto.idProducto,
            "proNombre":producto.proNombre, 
            "proPrecio":producto.proPrecio, 
            "categoria":{
                "idCategoria":producto.categoria.idCategoria,
                "catNombre":producto.categoria.catNombre 
                } 
        }
        mensaje="Datos del producto"
    except exc.SQLAlchemyError as error:
         mensaje("Problemas al consultar")
    return {"mensaje":mensaje,"producto":productoJson}

@app.route("/agregarProductoJson",methods=["POST"])
def agregarProductoJson():
    try:
        datos=request.get_json(force=True)
        codigo = int(datos["codigo"])
        nombre = datos["nombre"]
        precio = int(datos["precio"])
        categoria = int(datos["categoria"])
        # creacion de objeto producto 
        producto =Producto(proCodigo=codigo,proNombre=nombre,proPrecio=precio,proCategoria=categoria)
        db.session.add(producto)
        db.session.commit()
        mensaje="Producto Agregado Correctamente"
        estado=True
    except exc.SQLAlchemyError as error:
         db.session.rollback()
         mensaje("Problemas al registrar")
    return {"mensaje":mensaje,"estado":estado} 

@app.route("/eliminarProductoJson",methods=["POST"])
def eliminarProductoJson():
    try:
        estado=False
        datos=request.get_json(force=True)
        idProducto=int(datos["idProducto"])
        producto=Producto.query.get(idProducto)
        db.session.delete(producto)
        db.session.commit()
        estado=True
        mensaje="Producto eliminado"
        nuevoArchivo=str(idProducto)+".jpg"
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"]+"/"+nuevoArchivo))
    except  exc.SQLAlchemyError as error:
        db.session.rollback()
        mensaje = "Problemas al eliminar"
    return {"mensaje":mensaje,"estado":estado}

@app.route("/actualizarProductoJson",methods=["POST"])
def actualizarProductoJson():
    try:
        estado=False
        datos=request.get_json(force=True)
        idProducto=int(datos["idProducto"])
        producto=Producto.query.get(idProducto)
        producto.proCodigo = int(datos["codigo"])
        producto.proNombre = datos["txtNombre"]
        producto.proPrecio = int(datos["txtPrecio"])
        producto.proCategoria = int(datos["cbCategoria"])
        db.session.commit()  
        estado=True
        mensaje="Producto actualizado"
    except  exc.SQLAlchemyError as error:
        db.session.rollback()
        mensaje = "Problemas al actualizre"
    return {"mensaje":mensaje,"estado":estado}     
        