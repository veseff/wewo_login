from seguridad import *

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

    with open("usuarios.txt", "a") as archivo:
        archivo.write(
        f"{usuario} + {hash_contraseña(contraseña)}\n"
    )

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
                    f"{usuario} + {hash_contraseña(nueva_contraseña)}\n"
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
            and hash_contraseña(contraseña)
                == contraseña_guardada
):

            print(f"Bienvenido {usuario}")
            print(f"Iniciaste sesión en el intento {i + 1}")

            return True, usuario

        if i < 2:
            print(f"Te quedan {2 - i} intentos")

        print("Usuario o contraseña incorrectos")

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