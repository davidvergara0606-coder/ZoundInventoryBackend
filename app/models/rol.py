from app.database.database import db

class Rol(db.Model):
    __tablename__ = 'rol'
    
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    
    
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)