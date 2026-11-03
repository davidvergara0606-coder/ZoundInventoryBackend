import pytest

from app.models import Movimiento


# ---- Usuarios ----

@pytest.mark.xfail(strict=True, reason=(
    "Hallazgo 1: /auth/registro no revisa si el correo ya existe; "
    "la base de datos rechaza el duplicado y la ruta responde 500 en lugar de 400."
))
def test_registro_con_correo_duplicado_responde_400(client, crear_usuario, datos_usuario):
    crear_usuario()

    respuesta = client.post("/auth/registro", json=datos_usuario(documento="2002"))

    assert respuesta.status_code == 400
    assert respuesta.get_json() == {"mensaje": "El correo ya está registrado"}


@pytest.mark.xfail(strict=True, reason=(
    "Hallazgo 5: ninguna ruta pide autenticación ni rol; "
    "cualquiera puede crear usuarios, aunque solo el administrador debería poder."
))
def test_crear_usuario_sin_credenciales_es_rechazado(client, datos_usuario):
    respuesta = client.post("/auth/crear-usuario", json=datos_usuario())

    assert respuesta.status_code in (401, 403)


@pytest.mark.xfail(strict=True, reason=(
    "Hallazgo 5: ninguna ruta pide autenticación ni rol; "
    "cualquiera puede eliminar usuarios, aunque solo el administrador debería poder."
))
def test_eliminar_usuario_sin_credenciales_es_rechazado(client, crear_usuario):
    crear_usuario()

    respuesta = client.delete("/auth/usuarios/1001")

    assert respuesta.status_code in (401, 403)


@pytest.mark.xfail(strict=True, reason=(
    "Hallazgo 6: si falta la contraseña, generate_password_hash falla y la ruta "
    "responde 500 en lugar de 400."
))
@pytest.mark.parametrize("ruta", ["/auth/registro", "/auth/crear-usuario"])
def test_crear_usuario_sin_password_responde_400(client, datos_usuario, ruta):
    datos = datos_usuario()
    del datos["password"]

    respuesta = client.post(ruta, json=datos)

    assert respuesta.status_code == 400


@pytest.mark.xfail(strict=True, reason=(
    "Hallazgo 6: si el usuario existe y no se envía contraseña, check_password_hash "
    "falla y la ruta responde 500 en lugar de 401."
))
def test_login_sin_password_de_un_usuario_existente_responde_401(client, crear_usuario):
    crear_usuario()

    respuesta = client.post("/auth/login", json={"documento": "1001"})

    assert respuesta.status_code == 401


@pytest.mark.xfail(strict=True, reason=(
    "Hallazgo 7: actualizar el perfil no revisa si el correo ya lo usa otro usuario; "
    "la base de datos rechaza el duplicado y la ruta responde 500 en lugar de 400."
))
def test_actualizar_perfil_con_correo_de_otro_usuario_responde_400(client, crear_usuario):
    crear_usuario()
    crear_usuario(documento="2002", correo="otro@zound.com")

    respuesta = client.put("/auth/perfil/actualizar/1001", json={"correo": "otro@zound.com"})

    assert respuesta.status_code == 400


@pytest.mark.xfail(strict=True, reason=(
    "Hallazgo 7: actualizar el perfil ignora primer_apellido; solo cambia nombre, correo y contraseña."
))
def test_actualizar_perfil_cambia_el_apellido(client, buscar_usuario, crear_usuario):
    crear_usuario()

    client.put("/auth/perfil/actualizar/1001", json={"primer_apellido": "Gómez"})

    assert buscar_usuario("1001")["primer_apellido"] == "Gómez"


# ---- Productos y stock ----

@pytest.mark.xfail(strict=True, reason=(
    "Hallazgo 2: get_or_404 está dentro de un try/except Exception, así que un "
    "producto inexistente responde 400 con un mensaje de error en lugar de 404."
))
def test_entrada_de_producto_inexistente_responde_404(client):
    respuesta = client.post("/productos/entrada", json={"id_producto": 999, "cantidad": 1})

    assert respuesta.status_code == 404


@pytest.mark.xfail(strict=True, reason=(
    "Hallazgo 3: las entradas, salidas y movimientos solo cambian el stock; "
    "nunca crean un registro en Movimiento."
))
def test_entrada_registra_un_movimiento(app, client, crear_producto):
    id_producto = crear_producto()

    client.post("/productos/entrada", json={"id_producto": id_producto, "cantidad": 1})

    with app.app_context():
        assert Movimiento.query.count() == 1


@pytest.mark.xfail(strict=True, reason=(
    "Hallazgo 4: se aceptan cantidades negativas; una entrada negativa resta stock."
))
def test_entrada_con_cantidad_negativa_es_rechazada(client, crear_producto):
    id_producto = crear_producto(stock_actual=5)

    respuesta = client.post("/productos/entrada", json={"id_producto": id_producto, "cantidad": -2})

    assert respuesta.status_code == 400
