from usuarios import (
    registrar_usuario,
    iniciar_sesion,
    cambiar_contraseña,
    actualizar_contraseña,
    menu_usuario
)
from logs import registrar_log

# menú principal
print("1. Registrarse")
print("2. Iniciar sesión")

opcion_menu = input("Seleccione una opción: ")

if opcion_menu == "1":

    registrar_usuario()

elif opcion_menu == "2":

    confirmacion, usuario = iniciar_sesion()

    if confirmacion:

        registrar_log(
            f"LOGIN EXITOSO - {usuario}"
        )

        menu_usuario(usuario)

    else:

        registrar_log(
            "LOGIN FALLIDO"
        )

        print("Se agotaron los intentos")