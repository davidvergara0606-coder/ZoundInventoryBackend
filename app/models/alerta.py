from app.database.database import db
from datetime import datetime

class Alerta(db.Model):
    __tablename__ = 'alerta'
    
    id_alerta = db.Column(db.Integer, primary_key=True)
    mensaje = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id_producto'), nullable=False)