import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.config.settings import Config
from app.database.database import db
from app.models import Categoria, Producto, Rol, Usuario  # importar app.models registra todos los modelos


@pytest.fixture()
def app(monkeypatch):
    """App de Flask con una base de datos SQLite vacía, creada para esta prueba."""
    # Config arma la URI de MySQL al importarse; se reemplaza antes de crear la app.
    monkeypatch.setattr(Config, "SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
    app = create_app()
    # PROPAGATE_EXCEPTIONS=False: un error no controlado llega como respuesta 500,
    # igual que en producción, en lugar de romper la prueba con una excepción.
    app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=False)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def roles(app):
    """Roles del sistema: 1 = administrador, 2 = bodeguero."""
    with app.app_context():
        db.session.add_all([
            Rol(id_rol=1, nombre="Administrador"),
            Rol(id_rol=2, nombre="Bodeguero"),
        ])
        db.session.commit()


@pytest.fixture()
def client(app, roles):
    """Cliente HTTP de pruebas, con los dos roles ya creados."""
    return app.test_client()


# --------------------------------------------------------------------------
# Usuarios
# --------------------------------------------------------------------------

@pytest.fixture()
def datos_usuario():
    """Fábrica de datos de usuario válidos; se puede cambiar cualquier campo."""
    def _datos(**cambios):
        datos = {
            "primer_nombre": "Ana",
            "primer_apellido": "Pérez",
            "tipo_documento": "CC",
            "documento": "1001",
            "correo": "ana@zound.com",
            "password": "Clave123",
            "id_rol": 1,
        }
        datos.update(cambios)
        return datos
    return _datos


@pytest.fixture()
def crear_usuario(app, roles, datos_usuario):
    """Guarda un usuario directo en la base (con la clave encriptada) y devuelve sus datos."""
    def _crear(**cambios):
        datos = datos_usuario(**cambios)
        guardado = {**datos, "password": generate_password_hash(datos["password"])}
        with app.app_context():
            db.session.add(Usuario(**guardado))
            db.session.commit()
        return datos
    return _crear


@pytest.fixture()
def buscar_usuario(app):
    """Lee un usuario directo de la base de datos como diccionario (o None si no existe)."""
    def _buscar(documento):
        with app.app_context():
            usuario = Usuario.query.filter_by(documento=documento).first()
            if usuario is None:
                return None
            return {
                "primer_nombre": usuario.primer_nombre,
                "primer_apellido": usuario.primer_apellido,
                "correo": usuario.correo,
                "password": usuario.password,
                "id_rol": usuario.id_rol,
            }
    return _buscar


# --------------------------------------------------------------------------
# Productos
# --------------------------------------------------------------------------

@pytest.fixture()
def categoria(app):
    """Categoría con id 1 (no hay ruta para crearlas, así que se guarda directo)."""
    with app.app_context():
        db.session.add(Categoria(id_categoria=1, nombre="Parlantes"))
        db.session.commit()
    return 1


@pytest.fixture()
def crear_producto(app, categoria):
    """Guarda un producto directo en la base y devuelve su id."""
    def _crear(nombre="Parlante Acton", stock_actual=10, stock_minimo=2):
        with app.app_context():
            producto = Producto(
                nombre=nombre,
                stock_actual=stock_actual,
                stock_minimo=stock_minimo,
                id_categoria=categoria,
            )
            db.session.add(producto)
            db.session.commit()
            return producto.id_producto
    return _crear


@pytest.fixture()
def stock_de(app):
    """Lee el stock actual de un producto directo de la base de datos."""
    def _stock(id_producto):
        with app.app_context():
            return db.session.get(Producto, id_producto).stock_actual
    return _stock
