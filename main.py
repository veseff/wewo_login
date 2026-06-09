from getpass import getpass
from datetime import datetime



usuario_registrado = input("Crea un usuario: ").strip()

while usuario_registrado.strip() == "":
    usuario_registrado = input("El usuario no puede estar vacío: ")

contraseña_correcta = getpass("Crea una contraseña: ")

while (
        len(contraseña_correcta) < 8
    or not any(c.isdigit() for c in contraseña_correcta)
    or not any(c.isupper() for c in contraseña_correcta)
    or not any(c.islower() for c in contraseña_correcta)
    or not any(not c.isalnum() for c in contraseña_correcta)
):
    print("La contraseña debe tener:")
    print("- 8 caracteres mínimo")
    print("- Una mayúscula")
    print("- Una minúscula")
    print("- Un número")
    print("- Un símbolo")

    contraseña_correcta = getpass("Crea una contraseña: ")

repetir = getpass("Repite la contraseña: ")

while repetir != contraseña_correcta:
    print("Las contraseñas no coinciden")
    repetir = getpass("Repite la contraseña: ")

with open("usuarios.txt", "a") as archivo:
    archivo.write(f"{usuario_registrado} + {contraseña_correcta}\n")

print("La contraseña tiene", len(contraseña_correcta), "caracteres")

confirmacion = False

for i in range(3):

    usuario = input("Ingrese su usuario: ").strip()
    contraseña = getpass("Ingrese su contraseña: ")

    if usuario == usuario_registrado and contraseña == contraseña_correcta:
        confirmacion = True

        print(f"Bienvenido {usuario}")
        print(f"Iniciaste sesión en el intento {i + 1}")

        break

    if i < 2:
        print(f"Te quedan {2 - i} intentos")
    

    if usuario != usuario_registrado:
        print("Usuario incorrecto")

    if contraseña != contraseña_correcta:
        print("Contraseña incorrecta")


if confirmacion:

    opcion = input("¿Desea cambiar la contraseña? (s/n): ").lower()

    if opcion == "s":

        nueva_contraseña = getpass("Nueva contraseña: ")

        while (
            len(nueva_contraseña) < 8
            or not any(c.isdigit() for c in nueva_contraseña)
            or not any(c.isupper() for c in nueva_contraseña)
            or not any(c.islower() for c in nueva_contraseña)
            or not any(not c.isalnum() for c in nueva_contraseña)
        ):
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

        contraseña_correcta = nueva_contraseña
        print("Contraseña cambiada correctamente")

    elif opcion == "n":
        print("La contraseña no fue modificada")

    else:
        print("Opción inválida")


if confirmacion:
    with open("log.txt", "a") as archivo:
        archivo.write(
            f"{usuario} - {datetime.now()}\n"
        )
else:
    print("Se agotaron los intentos")
    with open("log.txt", "a") as archivo:
        archivo.write(
        f"Intento fallido - {datetime.now()}\n"
    )
        