import threading
import os
import time


# Variáveis globais
def setup_global():
    global redistribution_points
    global vehicles
    global packages_in_transit

    redistribution_points = []
    vehicles = []
    packages_in_transit = threading.Event()  # verifica se ainda há encomendas a entregar
    packages_in_transit.set()  # Inicialmente, há encomendas para entregar (evitar erros)


def log_event(message, file_path):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        with open(file_path, 'a') as file:
            file.write(log_entry)


if __name__ == "__main__":
    pass