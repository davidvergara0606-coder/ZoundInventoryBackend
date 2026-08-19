from app.database.database import db
from datetime import datetime

class Movimiento(db.Model):
    __tablename__ = 'movimiento'
    
    id_movimiento = db.Column(db.Integer, primary_key=True)
    tipo_movimiento = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(255))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)