from flask import Blueprint, request, jsonify
from app.database.database import db
from app.models.usuario import Usuario
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/admin/registro', methods=['POST'])
def registro_admin():
    data = request.json
    
    admin_id = data.get('admin_id') 
    admin = Usuario.query.get(admin_id)
    
    if not admin or admin.id_rol != 1:
        return jsonify({"mensaje": "Acceso denegado: Solo administradores pueden registrar usuarios"}), 403


    password_encriptada = generate_password_hash(data['password'])
    
    nuevo_usuario = Usuario(
        primer_nombre=data['primer_nombre'],
        primer_apellido=data['primer_apellido'],
        tipo_documento=data['tipo_documento'],
        documento=data['documento'],
        correo=data['correo'], 
        password=password_encriptada,
        id_rol=data['id_rol']
    )
    
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({"mensaje": "Usuario registrado exitosamente"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    usuario = Usuario.query.filter_by(documento=data['documento']).first()
    

    if usuario and check_password_hash(usuario.password, data['password']):
        return jsonify({"mensaje": "Login exitoso", "usuario": usuario.primer_nombre}), 200
    else:
        return jsonify({"mensaje": "Credenciales inválidas"}), 401