
import threading
import time
import random
from controle import packages_in_transit

# Função de ponto de redistribuição
class RedistributionPoint(threading.Thread):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.queue = []
        self.lock = threading.Lock()
        self.sem = threading.Semaphore(0)
        self.running = True  # Variável para controlar a execução da thread

    def run(self):
        while self.running:
            time.sleep(0.5)  # Controla o ciclo da thread, pelo que entendi evita consumir 100% da CPU

    def add_package(self, package):
        with self.lock:
            self.queue.append(package)
            self.sem.release()  # Incrementa o semáforo, indicando nova encomenda
            packages_in_transit.set()  # Indica que ainda há encomendas em trânsito

    def dispatch_package(self):
        self.sem.acquire()
        with self.lock:
            if self.queue:
                return self.queue.pop(0)
        return None

    def stop(self):
        self.running = False  # Permite parar a thread de forma controlada


# classe para os carros
class Vehicle(threading.Thread):
    def __init__(self, id, capacity, points):
        super().__init__()
        self.id = id
        self.capacity = capacity
        self.points = points
        self.current_point = random.choice(self.points)
        self.load = []

    def run(self):
        while packages_in_transit.is_set():
            
            # Move para o próximo ponto
            next_point = self.points[(self.points.index(self.current_point) + 1) % len(self.points)]
            print(f"[{time.strftime('%H:%M:%S')}] Veículo {self.id} partindo do ponto {self.current_point.id} para o ponto {next_point.id}")
            time.sleep(random.uniform(0.5, 2))  # Tempo de viagem lento entre 2 e 5 segundos

            # Carrega encomendas no ponto atual
            self.load.clear()
            for _ in range(self.capacity):
                package = self.current_point.dispatch_package()
                if package:
                    self.load.append(package)
                    package.log_event(f"Carregado no veículo {self.id} no ponto {self.current_point.id}")
                    print(f"[{time.strftime('%H:%M:%S')}] Carregado no veículo {self.id} no ponto {self.current_point.id}")
                    time.sleep(random.uniform(0.5, 3))  # Tempo de carregamento de cada encomenda

            # Descarrega encomendas no ponto de destino
            for package in self.load[:]:
                if package.destination == next_point:
                    package.log_event(f"Descarregado no ponto {next_point.id}")
                    print(f"Descarregado no ponto {next_point.id}")
                    self.load.remove(package)
                    package.stop()  # Faz a thread do pacote parar corretamente

            # Atualiza o ponto atual
            self.current_point = next_point

            # Verifica se ainda há encomendas em trânsito
            if not any(point.queue for point in self.points) and not self.load:
                packages_in_transit.clear()  # Encerra se todas as encomendas foram entregues


# classe para as encomendas
class Package(threading.Thread):
    def __init__(self, id, origin, destination):
        super().__init__()
        self.id = id
        self.origin = origin
        self.destination = destination
        self.file_path = f"Pacote_{self.id}_log.txt"
        self.origin.add_package(self)
        self.started = False  # Para controlar a criação do pacote
        self.lock = threading.Lock()
        self.start()  # Inicia a thread

    def run(self):
        if not self.started:
            self.started = True
            self.log_event(f"Encomenda criada no ponto {self.origin.id} com destino ao ponto {self.destination.id}")
            print(f"Encomenda criada no ponto {self.origin.id} com destino ao ponto {self.destination.id}")

    def log_event(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.file_path, 'a') as file:
            file.write(log_entry)

    def stop(self):
        """Método para parar a thread após o pacote ser entregue"""
        self.log_event(f"Encomenda {self.id} finalizada")
        print(f"Encomenda {self.id} finalizada")
        self.join()  # Aguarda a thread do pacote finalizar corretamente


