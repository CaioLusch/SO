import threading
import os

# Variáveis globais
redistribution_points = []
vehicles = []
packages_in_transit = threading.Event()  # verifica se ainda há encomendas a entregar
packages_in_transit.set()  # Inicialmente, há encomendas para entregar (evitar erros)