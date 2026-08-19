from app.database.database import db

class Proveedor(db.Model):
    __tablename__ = 'proveedor'
    
    id_proveedor = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100))
    
    