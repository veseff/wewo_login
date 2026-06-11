from seguridad import *
from logs import (
    registrar_log,
    ver_historial
    )
# crea un usuario
def crear_usuario():
    usuario = input("Crea un usuario: ").strip()

    while usuario == "":
        usuario = input("El usuario no puede estar vacío: ").strip()

    return usuario

# registra un usuario nuevo
def registrar_usuario():

    usuario = crear_usuario()

    while buscar_usuario(usuario) is not None:

        usuario = input(
            "Ese usuario ya existe. Elija otro: "
        ).strip()

    contraseña = crear_contraseña()

    salt = generar_salt()

    hash_guardado = hash_contraseña(
        contraseña,
        salt
    )

    with open("usuarios.txt", "a") as archivo:

        archivo.write(
            f"{usuario} + {salt} + {hash_guardado}\n"
        )

    registrar_log(
        f"USUARIO CREADO - {usuario}"
    )

    print("Usuario registrado correctamente")

    return usuario

# busca un usuario en usuarios.txt
def buscar_usuario(usuario_buscado):

    try:

        with open("usuarios.txt", "r") as archivo:

            for linea in archivo:

                usuario, salt, hash_guardado = (
                    linea.strip().split(" + ")
                )

                if usuario == usuario_buscado:

                    return salt, hash_guardado

    except FileNotFoundError:

        return None

    return None

# actualiza la contraseña de un usuario
def actualizar_contraseña(
    usuario_buscado,
    nueva_contraseña
):

    lineas_actualizadas = []

    with open("usuarios.txt", "r") as archivo:

        for linea in archivo:

            usuario, salt, hash_guardado = (
                linea.strip().split(" + ")
            )

            if usuario == usuario_buscado:

                nuevo_salt = generar_salt()

                nuevo_hash = hash_contraseña(
                    nueva_contraseña,
                    nuevo_salt
                )

                lineas_actualizadas.append(
                    f"{usuario} + {nuevo_salt} + {nuevo_hash}\n"
                )

            else:

                lineas_actualizadas.append(
                    linea
                )

    with open("usuarios.txt", "w") as archivo:

        archivo.writelines(
            lineas_actualizadas
        )

# sistema de login
def iniciar_sesion():

    max_intentos = 3

    for i in range(max_intentos):

        usuario = input(
            "Ingrese su usuario: "
        ).strip()

        contraseña = getpass(
            "Ingrese su contraseña: "
        )

        datos = buscar_usuario(usuario)

        if datos is not None:

            salt, hash_guardado = datos

            if (
                hash_contraseña(
                    contraseña,
                    salt
                )
                == hash_guardado
            ):

                print(f"Bienvenido {usuario}")

                return True, usuario

        print(
            "Usuario o contraseña incorrectos"
        )

        if i < max_intentos - 1:

            print(
                f"Te quedan {max_intentos - 1 - i} intentos"
            )

    return False, None

# cambia la contraseña actual del usuario logueado
def cambiar_contraseña():

    nueva_contraseña = getpass("Nueva contraseña: ")

    while not validar_contraseña(nueva_contraseña):
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

    lineas = []

    with open("usuarios.txt", "r") as archivo:

        for linea in archivo:

            usuario, contraseña = (
                linea.strip().split(" + ")
            )

            if usuario != usuario_buscado:
                lineas.append(linea)

    with open("usuarios.txt", "w") as archivo:
        archivo.writelines(lineas)

def menu_usuario(usuario):

    while True:

        print("\n=== MENÚ USUARIO ===")
        print("1. Cambiar contraseña")
        print("2. Ver historial")
        print("3. Eliminar usuario")
        print("4. Cerrar sesión")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":

            nueva = cambiar_contraseña()

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

                eliminar_usuario(usuario)

                registrar_log(
                    f"USUARIO ELIMINADO - {usuario}"
                )

                print("Usuario eliminado")

                break

        elif opcion == "4":

            registrar_log(
                f"CIERRE SESIÓN - {usuario}"
            )

            print("Sesión cerrada")

            break

        else:
            print("Opción inválida")