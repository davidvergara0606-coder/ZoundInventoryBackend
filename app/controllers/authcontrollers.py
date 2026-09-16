from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.database import db
from app.models.usuario import Usuario

def registrar_usuario_service(data):

    if Usuario.query.filter_by(documento=data.get('documento')).first():
        return {"mensaje": "El documento ya está registrado"}, 400
    
    if Usuario.query.filter_by(correo=data.get('correo')).first():
        return {"mensaje": "El correo ya está registrado"}, 400

    password_encriptada = generate_password_hash(data.get('password'))
    
    nuevo_usuario = Usuario(
        primer_nombre=data.get('primer_nombre'),
        primer_apellido=data.get('primer_apellido'),
        tipo_documento=data.get('tipo_documento'),
        documento=data.get('documento'),
        correo=data.get('correo'),
        password=password_encriptada,
        id_rol=data.get('id_rol')
    )

    db.session.add(nuevo_usuario)
    db.session.commit()
    return {"mensaje": "Usuario creado exitosamente"}, 201

def login_usuario_service(data):
    documento = data.get('documento')
    password = data.get('password')

    usuario = Usuario.query.filter_by(documento=documento).first()

    if usuario and check_password_hash(usuario.password, password):
        return {
            "mensaje": "Login exitoso",
            "usuario": usuario.primer_nombre,
            "id_rol": str(usuario.id_rol)  
        }, 200
    
    return {"mensaje": "Credenciales inválidas"}, 401