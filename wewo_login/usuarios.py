from getpass import getpass
import os
from pathlib import Path

from seguridad import (
    crear_contraseña,
    generar_salt,
    hash_contraseña,
    validar_contraseña,
    validar_usuario,
    verificar_contraseña
)
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
ARCHIVO_USUARIOS = Path(__file__).with_name("usuarios.txt")
SIN_BLOQUEO = "Sin bloqueo"


def fecha_actual():
    return datetime.now().strftime(FORMATO_FECHA)


def abrir_archivo_usuarios(modo):
    def opener(ruta, flags):
        return os.open(ruta, flags, 0o600)

    archivo = open(ARCHIVO_USUARIOS, modo, opener=opener)
    os.chmod(ARCHIVO_USUARIOS, 0o600)
    return archivo


def formatear_fecha(fecha):
    return fecha.strftime(FORMATO_FECHA)


def leer_fecha(fecha):
    if fecha in ("", SIN_BLOQUEO):
        return None

    try:
        return datetime.strptime(fecha, FORMATO_FECHA)
    except ValueError:
        return None


def leer_intentos(intentos_fallidos):
    try:
        return int(intentos_fallidos)
    except (TypeError, ValueError):
        return 0


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
    ultimo_login="Nunca",
    intentos_fallidos=0,
    bloqueado_hasta=SIN_BLOQUEO
):
    return {
        "usuario": usuario,
        "salt": salt,
        "hash": hash_guardado,
        "rol": rol,
        "fecha_creacion": fecha_creacion or fecha_actual(),
        "ultimo_login": ultimo_login,
        "intentos_fallidos": leer_intentos(intentos_fallidos),
        "bloqueado_hasta": bloqueado_hasta
    }


def leer_usuarios():
    usuarios = []

    try:
        with abrir_archivo_usuarios("r") as archivo:
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

                elif len(partes) == 8:
                    usuarios.append(
                        crear_registro_usuario(
                            partes[0],
                            partes[1],
                            partes[2],
                            rol=partes[3],
                            fecha_creacion=partes[4],
                            ultimo_login=partes[5],
                            intentos_fallidos=partes[6],
                            bloqueado_hasta=partes[7]
                        )
                    )

    except FileNotFoundError:
        pass

    return usuarios


def guardar_usuarios(usuarios):
    with abrir_archivo_usuarios("w") as archivo:
        for datos in usuarios:
            archivo.write(
                f"{datos['usuario']} + "
                f"{datos['salt']} + "
                f"{datos['hash']} + "
                f"{datos['rol']} + "
                f"{datos['fecha_creacion']} + "
                f"{datos['ultimo_login']} + "
                f"{datos['intentos_fallidos']} + "
                f"{datos['bloqueado_hasta']}\n"
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
    datos = obtener_usuario(usuario)

    if datos is not None:
        bloqueado_hasta = leer_fecha(datos["bloqueado_hasta"])

        if bloqueado_hasta is None:
            return False

        if datetime.now() >= bloqueado_hasta:
            actualizar_estado_login(usuario, intentos_fallidos=0, bloqueado_hasta=SIN_BLOQUEO)
            return False

        segundos = int((bloqueado_hasta - datetime.now()).total_seconds())
        print(f"Usuario bloqueado. Intente otra vez en {segundos} segundos.")
        return True

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

    datos = obtener_usuario(usuario)

    if datos is not None:
        intentos = datos["intentos_fallidos"] + 1
        bloqueado_hasta = SIN_BLOQUEO

        if intentos >= MAX_INTENTOS:
            bloqueado_hasta = formatear_fecha(datetime.now() + TIEMPO_BLOQUEO)
            registrar_log(f"USUARIO BLOQUEADO - {usuario}")
            print(f"Demasiados intentos fallidos. Bloqueado por {TIEMPO_BLOQUEO.seconds} segundos.")

        actualizar_estado_login(
            usuario,
            intentos_fallidos=intentos,
            bloqueado_hasta=bloqueado_hasta
        )
        return

    INTENTOS_FALLIDOS[usuario] = INTENTOS_FALLIDOS.get(usuario, 0) + 1

    if INTENTOS_FALLIDOS[usuario] >= MAX_INTENTOS:
        BLOQUEOS[usuario] = datetime.now() + TIEMPO_BLOQUEO
        registrar_log(f"USUARIO BLOQUEADO - {usuario}")
        print(f"Demasiados intentos fallidos. Bloqueado por {TIEMPO_BLOQUEO.seconds} segundos.")


def limpiar_intentos(usuario):
    INTENTOS_FALLIDOS.pop(usuario, None)
    BLOQUEOS.pop(usuario, None)
    actualizar_estado_login(usuario, intentos_fallidos=0, bloqueado_hasta=SIN_BLOQUEO)


def actualizar_estado_login(usuario_buscado, intentos_fallidos, bloqueado_hasta):
    usuarios = leer_usuarios()

    for datos in usuarios:
        if datos["usuario"] == usuario_buscado:
            datos["intentos_fallidos"] = intentos_fallidos
            datos["bloqueado_hasta"] = bloqueado_hasta

    guardar_usuarios(usuarios)


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

        if usuario_bloqueado(usuario):
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
        print("2. Eliminar usuario")

        if es_admin(usuario):
            print("3. Menú admin")
            print("4. Cerrar sesión")
        else:
            print("3. Cerrar sesión")

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

        elif opcion == "3" and es_admin(usuario):

            menu_admin(usuario)

        elif (
            opcion == "3" and not es_admin(usuario)
            or opcion == "4" and es_admin(usuario)
        ):

            registrar_log(
                f"CIERRE SESIÓN - {usuario}"
            )

            print("Sesión cerrada")

            break

        else:
            print("Opción inválida")
