from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.database import db
from app.models.usuario import Usuario
from app.models.producto import Producto

auth_bp = Blueprint('auth', __name__)
productos_bp = Blueprint('productos_bp', __name__)

@auth_bp.route('/registro', methods=['POST'])
def registro():
    data = request.get_json()
    
    if Usuario.query.filter_by(documento=data.get('documento')).first():
        return jsonify({"mensaje": "El documento ya está registrado"}), 400
    
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
    
    return jsonify({"mensaje": "Usuario creado exitosamente"}), 201

@auth_bp.route('/crear-usuario', methods=['POST'])
def crear_usuario_por_admin():
    data = request.get_json()
    
    if Usuario.query.filter_by(documento=data.get('documento')).first():
        return jsonify({"mensaje": "El documento ya está registrado"}), 400
    
    if Usuario.query.filter_by(correo=data.get('correo')).first():
        return jsonify({"mensaje": "El correo ya está registrado"}), 400

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
    
    return jsonify({"mensaje": "Usuario creado exitosamente por el Administrador"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    documento = data.get('documento')
    password = data.get('password')

    usuario = Usuario.query.filter_by(documento=documento).first()

    if usuario and check_password_hash(usuario.password, password):
        return jsonify({
            "mensaje": "Login exitoso",
            "id": usuario.documento,  
            "usuario": usuario.primer_nombre,
            "id_rol": str(usuario.id_rol) 
        }), 200
    
    return jsonify({"mensaje": "Credenciales inválidas"}), 401

@auth_bp.route('/perfil/<documento>', methods=['GET'])
def obtener_perfil(documento):
    usuario = Usuario.query.filter_by(documento=documento).first()
    if not usuario:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404
    
    return jsonify({
        "primer_nombre": usuario.primer_nombre,
        "primer_apellido": usuario.primer_apellido,
        "correo": usuario.correo,
        "documento": usuario.documento,
        "id_rol": usuario.id_rol
    }), 200

@auth_bp.route('/perfil/actualizar/<documento>', methods=['PUT'])
def actualizar_perfil(documento):
    data = request.get_json()
    usuario = Usuario.query.filter_by(documento=documento).first()
    
    if not usuario:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404

    if 'primer_nombre' in data:
        usuario.primer_nombre = data['primer_nombre']
    if 'correo' in data:
        usuario.correo = data['correo']
    
    password_plana = data.get('password')
    if password_plana and password_plana.strip() != "":
        usuario.password = generate_password_hash(password_plana)

    db.session.commit()
    return jsonify({"mensaje": "Perfil actualizado exitosamente"}), 200

@auth_bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    resultado = []
    for u in usuarios:
        resultado.append({
            "documento": u.documento,
            "primer_nombre": u.primer_nombre,
            "primer_apellido": u.primer_apellido,
            "correo": u.correo,
            "id_rol": u.id_rol
        })
    return jsonify(resultado), 200

@auth_bp.route('/usuarios/<documento>', methods=['DELETE'])
def eliminar_usuario(documento):
    usuario = Usuario.query.filter_by(documento=documento).first_or_404()
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({"mensaje": "Usuario eliminado correctamente"}), 200


@productos_bp.route('/productos', methods=['POST'])
def crear_producto():
    data = request.get_json()

    if Producto.query.filter_by(nombre=data.get('nombre')).first():
        return jsonify({"mensaje": "El producto ya existe"}), 400

    nuevo_producto = Producto(
        nombre=data.get('nombre'),
        stock_actual=data.get('stock_actual'),
        stock_minimo=data.get('stock_minimo'),
        id_categoria=data.get('id_categoria')
    )

    db.session.add(nuevo_producto)
    db.session.commit()

    return jsonify({
        "mensaje": "Producto creado correctamente",
        "id_producto": nuevo_producto.id_producto
    }), 201

@productos_bp.route('/productos', methods=['GET'])
def obtener_productos():
    productos = Producto.query.all()
    resultado = []

    for p in productos:
        resultado.append({
            "id_producto": p.id_producto,
            "codigo": f"P{p.id_producto:03d}", 
            "nombre": p.nombre,
            "stock_actual": p.stock_actual,
            "stock_minimo": p.stock_minimo,
            "id_categoria": p.id_categoria,
            "categoria": "General" 
        })

    return jsonify(resultado), 200


@productos_bp.route('/productos/alertas', methods=['GET'])
def obtener_alertas_stock():

    productos = Producto.query.filter(Producto.stock_actual <= Producto.stock_minimo).all()
    resultado = [{
        "id_producto": p.id_producto,
        "codigo": f"P{p.id_producto:03d}",
        "nombre": p.nombre,
        "categoria": "General",
        "stock_actual": p.stock_actual,
        "stock_minimo": p.stock_minimo
    } for p in productos]
    return jsonify(resultado), 200

@productos_bp.route('/productos/<int:id_producto>', methods=['PUT'])
def actualizar_producto(id_producto):
    producto = Producto.query.get_or_404(id_producto)
    data = request.get_json()

    producto.nombre = data.get("nombre", producto.nombre)
    producto.stock_actual = data.get("stock_actual", producto.stock_actual)
    producto.stock_minimo = data.get("stock_minimo", producto.stock_minimo)
    producto.id_categoria = data.get("id_categoria", producto.id_categoria)

    db.session.commit()

    return jsonify({"mensaje": "Producto actualizado correctamente"}), 200

@productos_bp.route('/productos/<int:id_producto>', methods=['DELETE'])
def eliminar_producto(id_producto):
    try:
        producto = Producto.query.get_or_404(id_producto)
        db.session.delete(producto)
        db.session.commit()
        return jsonify({"mensaje": "Producto eliminado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        print("Error al eliminar:", str(e))
        return jsonify({"mensaje": "No se puede eliminar el producto porque tiene movimientos registrados en el inventario."}), 400

@productos_bp.route('/categorias', methods=['GET'])
def obtener_categorias():
    return jsonify([{"id_categoria": 1, "nombre": "General"}]), 200


@productos_bp.route('/movimientos', methods=['POST'])
def registrar_movimiento():
    data = request.get_json()
    
    try:
        producto = Producto.query.get_or_404(data.get('id_producto'))
        cantidad = int(data.get('cantidad'))
        
        tipo = data.get('tipo_movimiento')
        if tipo == 'entrada':
            producto.stock_actual += cantidad
        elif tipo == 'salida':
            if producto.stock_actual < cantidad:
                return jsonify({"mensaje": "Stock insuficiente para la salida"}), 400
            producto.stock_actual -= cantidad
        else:
            return jsonify({"mensaje": "Tipo de movimiento inválido"}), 400
            
        db.session.commit()
        return jsonify({"mensaje": "Movimiento registrado con éxito"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"mensaje": f"Error al registrar movimiento: {str(e)}"}), 400


@productos_bp.route('/reportes/<tipo>', methods=['GET'])
def obtener_reportes(tipo):
    productos = Producto.query.all()
    
    if tipo == 'stock':
        resultado = [{"codigo": f"P{p.id_producto:03d}", "nombre": p.nombre, "categoria": "General", "stock": p.stock_actual} for p in productos]
    elif tipo == 'garantia':
        resultado = [{"codigo": "P012", "nombre": "Manos libres", "categoria": "Periférico", "observacion": "Garantía de fábrica activa"}]
    elif tipo == 'devoluciones':
        resultado = [{"codigo": "P005", "nombre": "Marshall Acton III", "categoria": "Hablante", "observacion": "Devolución por cambio de referencia"}]
    else:
        resultado = []
        
    return jsonify(resultado), 200