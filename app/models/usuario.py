from app.database.database import db

class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    id_usuario = db.Column(db.Integer, primary_key=True)
    primer_nombre = db.Column(db.String(50), nullable=False)
    primer_apellido = db.Column(db.String(50), nullable=False)
    tipo_documento = db.Column(db.String(20), nullable=False)
    documento = db.Column(db.String(50), nullable=False, unique=True)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('rol.id_rol'), nullable=False)
    
   
    movimientos = db.relationship('Movimiento', backref='usuario', lazy=True)