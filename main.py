from getpass import getpass
from datetime import datetime

#crea un usuario
def crear_usuario():
    usuario = input("Crea un usuario: ").strip()

    while usuario == "":
        usuario = input("El usuario no puede estar vacío: ").strip()

    return usuario

#valida una contraseña
def validar_contraseña(contraseña):
    return (
        len(contraseña) >= 8
        and any(c.isdigit() for c in contraseña)
        and any(c.isupper() for c in contraseña)
        and any(c.islower() for c in contraseña)
        and any(not c.isalnum() for c in contraseña)
    )

#crea una contraseña
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
#cambia la contraseña actual del usuario logeado
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
#sistema de logeo 
def iniciar_sesion(usuario_registrado, contraseña_correcta):

    for i in range(3):

        usuario = input("Ingrese su usuario: ").strip()
        contraseña = getpass("Ingrese su contraseña: ")

        if usuario == usuario_registrado and contraseña == contraseña_correcta:

            print(f"Bienvenido {usuario}")
            print(f"Iniciaste sesión en el intento {i + 1}")

            return True, usuario

        if i < 2:
            print(f"Te quedan {2 - i} intentos")

        if usuario != usuario_registrado:
            print("Usuario incorrecto")

        if contraseña != contraseña_correcta:
            print("Contraseña incorrecta")

    return False, None

def registrar_usuario():

    usuario = crear_usuario()
    contraseña = crear_contraseña()

    with open("usuarios.txt", "a") as archivo:
        archivo.write(f"{usuario} + {contraseña}\n")

    print("Usuario registrado correctamente")

#logs de los registro
def registrar_log(texto):
    with open("log.txt", "a") as archivo:
        archivo.write(f"{texto} - {datetime.now()}\n")


print("1. Registrarse")
print("2. Iniciar sesión")

opcion_menu = input("Seleccione una opción: ")

if opcion_menu == "1":

    registrar_usuario()

elif opcion_menu == "2":

    usuario_registrado = crear_usuario()
    contraseña_correcta = crear_contraseña()

    print("La contraseña tiene", len(contraseña_correcta), "caracteres")

    confirmacion, usuario = iniciar_sesion(
        usuario_registrado,
        contraseña_correcta
    )

    if confirmacion:

        opcion = input(
            "¿Desea cambiar la contraseña? (s/n): "
        ).lower()

        if opcion == "s":
            contraseña_correcta = cambiar_contraseña()

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


print("La contraseña tiene", len(contraseña_correcta), "caracteres")

#bucle principal
confirmacion, usuario = iniciar_sesion(
    usuario_registrado,
    contraseña_correcta
)
#cambio de contraseña
if confirmacion:

    opcion = input("¿Desea cambiar la contraseña? (s/n): ").lower()

    if opcion == "s":
        contraseña_correcta = cambiar_contraseña()

    elif opcion == "n":
        print("La contraseña no fue modificada")

    else:
        print("Opción inválida")
#registra los log
if confirmacion:
    registrar_log(usuario)
else:
    print("Se agotaron los intentos")
    registrar_log("Intento fallido")