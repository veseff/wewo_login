from seguridad import *
from logs import (
    registrar_log,
    ver_historial
)
from datetime import datetime, timedelta


INTENTOS_FALLIDOS = {}
BLOQUEOS = {}
MAX_INTENTOS = 3
TIEMPO_BLOQUEO = timedelta(seconds=30)
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"


def fecha_actual():
    return datetime.now().strftime(FORMATO_FECHA)


# crea un usuario
def crear_usuario():
    usuario = input("Crea un usuario: ").strip()

    while not validar_usuario(usuario):
        print("El usuario debe tener entre 3 y 20 caracteres.")
        print("Solo puede usar letras, números, _ o -.")
        usuario = input("Crea un usuario: ").strip()

    return usuario


def crear_registro_usuario(
    usuario,
    salt,
    hash_guardado,
    rol="usuario",
    fecha_creacion=None,
    ultimo_login="Nunca"
):
    return {
        "usuario": usuario,
        "salt": salt,
        "hash": hash_guardado,
        "rol": rol,
        "fecha_creacion": fecha_creacion or fecha_actual(),
        "ultimo_login": ultimo_login
    }


def leer_usuarios():
    usuarios = []

    try:
        with open("usuarios.txt", "r") as archivo:
            for linea in archivo:
                partes = linea.strip().split(" + ")

                if len(partes) == 3:
                    rol = "admin" if len(usuarios) == 0 else "usuario"
                    usuarios.append(
                        crear_registro_usuario(
                            partes[0],
                            partes[1],
                            partes[2],
                            rol=rol,
                            fecha_creacion="Desconocida"
                        )
                    )

                elif len(partes) == 6:
                    usuarios.append(
                        crear_registro_usuario(
                            partes[0],
                            partes[1],
                            partes[2],
                            rol=partes[3],
                            fecha_creacion=partes[4],
                            ultimo_login=partes[5]
                        )
                    )

    except FileNotFoundError:
        pass

    return usuarios


def guardar_usuarios(usuarios):
    with open("usuarios.txt", "w") as archivo:
        for datos in usuarios:
            archivo.write(
                f"{datos['usuario']} + "
                f"{datos['salt']} + "
                f"{datos['hash']} + "
                f"{datos['rol']} + "
                f"{datos['fecha_creacion']} + "
                f"{datos['ultimo_login']}\n"
            )


def obtener_usuario(usuario_buscado):
    for datos in leer_usuarios():
        if datos["usuario"] == usuario_buscado:
            return datos

    return None


# registra un usuario nuevo
def registrar_usuario():

    usuario = crear_usuario()

    while buscar_usuario(usuario) is not None:

        usuario = input(
            "Ese usuario ya existe. Elija otro: "
        ).strip()

        while not validar_usuario(usuario):
            print("El usuario debe tener entre 3 y 20 caracteres.")
            print("Solo puede usar letras, números, _ o -.")
            usuario = input("Elija otro usuario: ").strip()

    contraseña = crear_contraseña()

    salt = generar_salt()

    hash_guardado = hash_contraseña(
        contraseña,
        salt
    )

    rol = "admin" if len(leer_usuarios()) == 0 else "usuario"

    usuarios = leer_usuarios()
    usuarios.append(
        crear_registro_usuario(
            usuario,
            salt,
            hash_guardado,
            rol=rol
        )
    )
    guardar_usuarios(usuarios)

    registrar_log(
        f"USUARIO CREADO - {usuario} - ROL {rol}"
    )

    print("Usuario registrado correctamente")
    print(f"Rol asignado: {rol}")

    return usuario


# busca un usuario en usuarios.txt
def buscar_usuario(usuario_buscado):
    datos = obtener_usuario(usuario_buscado)

    if datos is None:
        return None

    return datos["salt"], datos["hash"]


def usuario_bloqueado(usuario):
    bloqueado_hasta = BLOQUEOS.get(usuario)

    if bloqueado_hasta is None:
        return False

    if datetime.now() >= bloqueado_hasta:
        del BLOQUEOS[usuario]
        INTENTOS_FALLIDOS[usuario] = 0
        return False

    segundos = int((bloqueado_hasta - datetime.now()).total_seconds())
    print(f"Usuario bloqueado. Intente otra vez en {segundos} segundos.")
    return True


def registrar_intento_fallido(usuario):
    if usuario == "":
        return

    INTENTOS_FALLIDOS[usuario] = INTENTOS_FALLIDOS.get(usuario, 0) + 1

    if INTENTOS_FALLIDOS[usuario] >= MAX_INTENTOS:
        BLOQUEOS[usuario] = datetime.now() + TIEMPO_BLOQUEO
        registrar_log(f"USUARIO BLOQUEADO - {usuario}")
        print(f"Demasiados intentos fallidos. Bloqueado por {TIEMPO_BLOQUEO.seconds} segundos.")


def limpiar_intentos(usuario):
    INTENTOS_FALLIDOS.pop(usuario, None)
    BLOQUEOS.pop(usuario, None)


def actualizar_ultimo_login(usuario_buscado):
    usuarios = leer_usuarios()

    for datos in usuarios:
        if datos["usuario"] == usuario_buscado:
            datos["ultimo_login"] = fecha_actual()

    guardar_usuarios(usuarios)


# actualiza la contraseña de un usuario
def actualizar_contraseña(
    usuario_buscado,
    nueva_contraseña
):

    usuarios = leer_usuarios()

    for datos in usuarios:
        if datos["usuario"] == usuario_buscado:
            nuevo_salt = generar_salt()

            nuevo_hash = hash_contraseña(
                nueva_contraseña,
                nuevo_salt
            )

            datos["salt"] = nuevo_salt
            datos["hash"] = nuevo_hash

    guardar_usuarios(usuarios)


# sistema de login
def iniciar_sesion():

    ultimo_usuario = None

    for i in range(MAX_INTENTOS):

        usuario = input(
            "Ingrese su usuario: "
        ).strip()

        ultimo_usuario = usuario

        if usuario_bloqueado(usuario):
            return False, usuario

        contraseña = getpass(
            "Ingrese su contraseña: "
        )

        datos = obtener_usuario(usuario)

        if datos is not None:
            if verificar_contraseña(
                contraseña,
                datos["salt"],
                datos["hash"]
            ):
                print(f"Bienvenido {usuario}")
                print(f"Rol: {datos['rol']}")
                print(f"Último inicio de sesión: {datos['ultimo_login']}")

                limpiar_intentos(usuario)
                actualizar_ultimo_login(usuario)

                return True, usuario

        print(
            "Usuario o contraseña incorrectos"
        )

        registrar_log(f"LOGIN FALLIDO - {usuario}")
        registrar_intento_fallido(usuario)

        if usuario in BLOQUEOS:
            return False, usuario

        if i < MAX_INTENTOS - 1:

            print(
                f"Te quedan {MAX_INTENTOS - 1 - i} intentos"
            )

    return False, ultimo_usuario


# cambia la contraseña actual del usuario logueado
def cambiar_contraseña(usuario):

    datos = obtener_usuario(usuario)

    if datos is None:
        print("No se encontró el usuario")
        return None

    contraseña_actual = getpass("Contraseña actual: ")

    if not verificar_contraseña(
        contraseña_actual,
        datos["salt"],
        datos["hash"]
    ):
        print("Contraseña actual incorrecta")
        registrar_log(f"CAMBIO CONTRASEÑA FALLIDO - {usuario}")
        return None

    nueva_contraseña = getpass("Nueva contraseña: ")

    while (
        not validar_contraseña(nueva_contraseña)
        or verificar_contraseña(nueva_contraseña, datos["salt"], datos["hash"])
    ):
        if verificar_contraseña(nueva_contraseña, datos["salt"], datos["hash"]):
            print("La nueva contraseña no puede ser igual a la actual")

        print("La contraseña debe tener:")
        print("- 8 caracteres mínimo")
        print("- Una mayúscula")
        print("- Una minúscula")
        print("- Un número")
        print("- Un símbolo")

        nueva_contraseña = getpass("Nueva contraseña: ")

    repetir = getpass("Repita la nueva contraseña: ")

    while repetir != nueva_contraseña:
        print("Las contraseñas no coinciden")
        repetir = getpass("Repita la nueva contraseña: ")

    print("Contraseña cambiada correctamente")

    return nueva_contraseña


def eliminar_usuario(usuario_buscado):

    usuarios = [
        datos
        for datos in leer_usuarios()
        if datos["usuario"] != usuario_buscado
    ]

    guardar_usuarios(usuarios)


def confirmar_contraseña(usuario):
    datos = obtener_usuario(usuario)

    if datos is None:
        return False

    contraseña = getpass("Confirme su contraseña: ")

    return verificar_contraseña(
        contraseña,
        datos["salt"],
        datos["hash"]
    )


def es_admin(usuario):
    datos = obtener_usuario(usuario)

    return datos is not None and datos["rol"] == "admin"


def listar_usuarios():
    print("\n=== USUARIOS ===")

    for datos in leer_usuarios():
        print(
            f"{datos['usuario']} | "
            f"rol: {datos['rol']} | "
            f"creado: {datos['fecha_creacion']} | "
            f"último login: {datos['ultimo_login']}"
        )


def cambiar_rol_usuario(usuario_actual):
    usuario_objetivo = input("Usuario a modificar: ").strip()
    datos_objetivo = obtener_usuario(usuario_objetivo)

    if datos_objetivo is None:
        print("No se encontró el usuario")
        return

    if usuario_objetivo == usuario_actual:
        print("No puede cambiar su propio rol")
        return

    nuevo_rol = input("Nuevo rol (admin/usuario): ").strip().lower()

    while nuevo_rol not in ("admin", "usuario"):
        nuevo_rol = input("Ingrese admin o usuario: ").strip().lower()

    usuarios = leer_usuarios()

    for datos in usuarios:
        if datos["usuario"] == usuario_objetivo:
            datos["rol"] = nuevo_rol

    guardar_usuarios(usuarios)
    registrar_log(
        f"CAMBIO ROL - {usuario_objetivo} - {nuevo_rol} - POR {usuario_actual}"
    )
    print("Rol actualizado")


def menu_admin(usuario):
    while True:
        print("\n=== MENÚ ADMIN ===")
        print("1. Listar usuarios")
        print("2. Cambiar rol de usuario")
        print("3. Ver historial")
        print("4. Volver")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            listar_usuarios()

        elif opcion == "2":
            cambiar_rol_usuario(usuario)

        elif opcion == "3":
            ver_historial()

        elif opcion == "4":
            break

        else:
            print("Opción inválida")


def menu_usuario(usuario):

    while True:

        print("\n=== MENÚ USUARIO ===")
        print("1. Cambiar contraseña")
        print("2. Ver historial")
        print("3. Eliminar usuario")

        if es_admin(usuario):
            print("4. Menú admin")
            print("5. Cerrar sesión")
        else:
            print("4. Cerrar sesión")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":

            nueva = cambiar_contraseña(usuario)

            if nueva is None:
                continue

            actualizar_contraseña(
                usuario,
                nueva
            )

            registrar_log(
                f"CAMBIO CONTRASEÑA - {usuario}"
            )

        elif opcion == "2":

            ver_historial()

        elif opcion == "3":

            confirmar = input(
                "¿Seguro? (s/n): "
            ).lower()

            if confirmar == "s":
                if not confirmar_contraseña(usuario):
                    print("Contraseña incorrecta. No se eliminó el usuario")
                    registrar_log(
                        f"ELIMINAR USUARIO FALLIDO - {usuario}"
                    )
                    continue

                eliminar_usuario(usuario)

                registrar_log(
                    f"USUARIO ELIMINADO - {usuario}"
                )

                print("Usuario eliminado")

                break

        elif opcion == "4" and es_admin(usuario):

            menu_admin(usuario)

        elif (
            opcion == "4" and not es_admin(usuario)
            or opcion == "5" and es_admin(usuario)
        ):

            registrar_log(
                f"CIERRE SESIÓN - {usuario}"
            )

            print("Sesión cerrada")

            break

        else:
            print("Opción inválida")
