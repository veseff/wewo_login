from getpass import getpass
from datetime import datetime


# crea un usuario
def crear_usuario():
    usuario = input("Crea un usuario: ").strip()

    while usuario == "":
        usuario = input("El usuario no puede estar vacío: ").strip()

    return usuario


# valida una contraseña
def validar_contraseña(contraseña):
    return (
        len(contraseña) >= 8
        and any(c.isdigit() for c in contraseña)
        and any(c.isupper() for c in contraseña)
        and any(c.islower() for c in contraseña)
        and any(not c.isalnum() for c in contraseña)
    )


# crea una contraseña
def crear_contraseña():
    contraseña = getpass("Crea una contraseña: ")

    while not validar_contraseña(contraseña):
        print("La contraseña debe tener:")
        print("- 8 caracteres mínimo")
        print("- Una mayúscula")
        print("- Una minúscula")
        print("- Un número")
        print("- Un símbolo")

        contraseña = getpass("Crea una contraseña: ")

    repetir = getpass("Repite la contraseña: ")

    while repetir != contraseña:
        print("Las contraseñas no coinciden")
        repetir = getpass("Repite la contraseña: ")

    return contraseña


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


# registra un usuario nuevo
def registrar_usuario():

    usuario = crear_usuario()

    while buscar_usuario(usuario) is not None:
        usuario = input(
        "Ese usuario ya existe. Elija otro: "
    ).strip()

    contraseña = crear_contraseña()

    with open("usuarios.txt", "a") as archivo:
        archivo.write(f"{usuario} + {contraseña}\n")

    print("Usuario registrado correctamente")

# busca un usuario en usuarios.txt
def buscar_usuario(usuario_buscado):

    try:
        with open("usuarios.txt", "r") as archivo:

            for linea in archivo:
                usuario, contraseña = linea.strip().split(" + ")

                if usuario == usuario_buscado:
                    return contraseña

    except FileNotFoundError:
        return None

    return None

# actualiza la contraseña de un usuario
def actualizar_contraseña(usuario_buscado, nueva_contraseña):

    lineas_actualizadas = []

    with open("usuarios.txt", "r") as archivo:

        for linea in archivo:

            usuario, contraseña = linea.strip().split(" + ")

            if usuario == usuario_buscado:
                lineas_actualizadas.append(
                    f"{usuario} + {nueva_contraseña}\n"
                )
            else:
                lineas_actualizadas.append(linea)

    with open("usuarios.txt", "w") as archivo:
        archivo.writelines(lineas_actualizadas)

# sistema de login
def iniciar_sesion():

    for i in range(3):

        usuario = input("Ingrese su usuario: ").strip()
        contraseña = getpass("Ingrese su contraseña: ")

        contraseña_guardada = buscar_usuario(usuario)

        if (
            contraseña_guardada is not None
            and contraseña == contraseña_guardada
        ):

            print(f"Bienvenido {usuario}")
            print(f"Iniciaste sesión en el intento {i + 1}")

            return True, usuario

        if i < 2:
            print(f"Te quedan {2 - i} intentos")

        print("Usuario o contraseña incorrectos")

    return False, None


# logs
def registrar_log(texto):
    with open("log.txt", "a") as archivo:
        archivo.write(f"{texto} - {datetime.now()}\n")


# menú principal
print("1. Registrarse")
print("2. Iniciar sesión")

opcion_menu = input("Seleccione una opción: ")

if opcion_menu == "1":

    registrar_usuario()

elif opcion_menu == "2":

    confirmacion, usuario = iniciar_sesion()

    if confirmacion:

        opcion = input(
            "¿Desea cambiar la contraseña? (s/n): "
        ).lower()

        if opcion == "s":

            nueva_contraseña = cambiar_contraseña()

            actualizar_contraseña(
                usuario,
                nueva_contraseña
            )
            print("Contraseña guardada correctamente")

        elif opcion == "n":
            print("La contraseña no fue modificada")

        else:
            print("Opción inválida")

    if confirmacion:
        registrar_log(usuario)
    else:
        print("Se agotaron los intentos")
        registrar_log("Intento fallido")

else:
    print("Opción inválida")