from app import db


class Producto(db.Model):
    __tablename__ = "productos"
    idProducto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    proCodigo = db.Column(db.Integer, unique=True, nullable=False)
    proNombre = db.Column(db.String(25), nullable=False)
    proPrecio = db.Column(db.Integer, nullable=False)
    # Atributo que representa la llave foranea en la base de datos
    proCategoria = db.Column(db.Integer, db.ForeignKey('categorias.idCategoria'), nullable=False)
    #Necesarios para la relacion 
    categoria=db.relationship("Categoria",backref=db.backref('categorias'),lazy=True)
    def __repr__(self):
        return f'{self.proNombre}'