from app.database.database import db
from datetime import datetime

class Devolucion(db.Model):
    __tablename__ = 'devolucion'

    id_devolucion = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id_producto'), nullable=False)
    observacion = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    producto = db.relationship('Producto')