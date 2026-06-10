from usuarios import *
from seguridad import *
from logs import *

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