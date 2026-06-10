from datetime import datetime

# logs
def registrar_log(texto):
    with open("log.txt", "a") as archivo:
        archivo.write(f"{texto} - {datetime.now()}\n")