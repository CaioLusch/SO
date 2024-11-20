import threading
import os

# Variáveis globais
def setup_global():
    global redistribution_points
    global vehicles
    global packages_in_transit

    redistribution_points = []
    vehicles = []
    packages_in_transit = threading.Event()  # verifica se ainda há encomendas a entregar
    packages_in_transit.set()  # Inicialmente, há encomendas para entregar (evitar erros)


if __name__ == "__main__":
    pass