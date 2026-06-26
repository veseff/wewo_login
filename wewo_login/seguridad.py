from getpass import getpass
import hashlib
import secrets
import re


PBKDF2_ITERACIONES = 200_000


def generar_salt():
    return secrets.token_hex(16)


def validar_usuario(usuario):
    return re.fullmatch(r"[A-Za-z0-9_-]{3,20}", usuario) is not None


def validar_contraseña(contraseña):
    return (
        len(contraseña) >= 8
        and any(c.isdigit() for c in contraseña)
        and any(c.isupper() for c in contraseña)
        and any(c.islower() for c in contraseña)
        and any(not c.isalnum() for c in contraseña)
    )


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


def hash_contraseña(contraseña, salt):
    hash_guardado = hashlib.pbkdf2_hmac(
        "sha256",
        contraseña.encode(),
        salt.encode(),
        PBKDF2_ITERACIONES
    ).hex()

    return f"pbkdf2_sha256${PBKDF2_ITERACIONES}${hash_guardado}"


def verificar_contraseña(contraseña, salt, hash_guardado):
    partes = hash_guardado.split("$")

    if len(partes) == 3 and partes[0] == "pbkdf2_sha256":
        try:
            iteraciones = int(partes[1])
        except ValueError:
            return False

        hash_calculado = hashlib.pbkdf2_hmac(
            "sha256",
            contraseña.encode(),
            salt.encode(),
            iteraciones
        ).hex()

        return secrets.compare_digest(hash_calculado, partes[2])

    # Compatibilidad con usuarios creados antes, usando sha256 simple.
    hash_viejo = hashlib.sha256(
        (salt + contraseña).encode()
    ).hexdigest()

    return secrets.compare_digest(hash_viejo, hash_guardado)
