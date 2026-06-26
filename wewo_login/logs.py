from datetime import datetime
import os
from pathlib import Path


ARCHIVO_LOG = Path(__file__).with_name("log.txt")


def abrir_log(modo):
    def opener(ruta, flags):
        return os.open(ruta, flags, 0o600)

    archivo = open(ARCHIVO_LOG, modo, opener=opener)
    os.chmod(ARCHIVO_LOG, 0o600)
    return archivo


# logs
def registrar_log(texto):

    with abrir_log("a") as archivo:

        archivo.write(
            f"{texto} - "
            f"{datetime.now()}\n"
        )

def ver_historial():

    try:

        with abrir_log("r") as archivo:

            print("\n=== HISTORIAL ===")

            for linea in archivo:
                print(linea.strip())

    except FileNotFoundError:
        print("No hay historial")
