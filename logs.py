from datetime import datetime

# logs
def registrar_log(texto):

    with open("log.txt", "a") as archivo:

        archivo.write(
            f"{texto} - "
            f"{datetime.now()}\n"
        )

def ver_historial():

    try:

        with open("log.txt", "r") as archivo:

            print("\n=== HISTORIAL ===")

            for linea in archivo:
                print(linea.strip())

    except FileNotFoundError:
        print("No hay historial")