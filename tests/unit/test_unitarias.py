from werkzeug.security import check_password_hash

def test_registro_crea_usuario_con_clave_encriptada(client, buscar_usuario, datos_usuario):
    datos = datos_usuario()
    respuesta = client.post("/auth/registro", json=datos)
    print(respuesta.status_code, respuesta.get_json()) 

    assert respuesta.status_code == 201
    assert respuesta.json == {"mensaje" : "Usuario creado exitosamente"}
    guardado = buscar_usuario(datos["documento"])
    print(guardado)
    assert guardado["password"] != datos["password"]
    assert check_password_hash(guardado["password"], datos["password"]) is True

def test_registro_crear_usuario_sin_clave(client, buscar_usuario, datos_usuario):
    datos = datos_usuario()
    del datos["password"]

    respuesta = client.post("/auth/registro", json=datos)
    print(respuesta.status_code, respuesta.get_json()) 

    assert respuesta.status_code == 400
    guardado = buscar_usuario(datos["documento"])
    assert respuesta.json ==  {"mensaje": "No se ha digitado el password"}

def test_registro_con_clave_vacia(client, buscar_usuario, datos_usuario):
    datos = datos_usuario()
    datos ["password"] = ""

    respuesta = client.post("/auth/registro", json=datos)
    print(respuesta.status_code, respuesta.get_json()) 

    assert respuesta.status_code == 400
    assert respuesta.json ==  {"mensaje": "No se ha digitado el password"}
    guardado = buscar_usuario(datos["documento"])
    assert guardado is None

def test_registro_clave_caracteres_minimos(client, buscar_usuario, datos_usuario):
    datos = datos_usuario()
    datos ["password"] = "clave12"

    respuesta = client.post("/auth/registro", json=datos)
    print(respuesta.status_code, respuesta.get_json()) 

    assert respuesta.status_code == 400
    assert respuesta.json ==  {"mensaje": "password muy corta"}
    guardado = buscar_usuario(datos["documento"])
    assert guardado is None

def test_registro_clave_caracteres_maximos(client, buscar_usuario, datos_usuario):
    datos = datos_usuario()
    datos ["password"] = "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0w"

    respuesta = client.post("/auth/registro", json=datos)
    print(respuesta.status_code, respuesta.get_json()) 

    assert respuesta.status_code == 400
    assert respuesta.json ==  {"mensaje": "password muy larga"}
    guardado = buscar_usuario(datos["documento"])
    assert guardado is None