from getpass import getpass
import hashlib

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

def hash_contraseña(contraseña):
    return hashlib.sha256(
        contraseña.encode()
    ).hexdigest()