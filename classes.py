import threading
import time
import random

import controle


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
        self.start()  # Inicia a thread

    def run(self):
        if not self.started:
            self.started = True
            controle.log_event(f"Encomenda criada no ponto {self.origin.id} com destino ao ponto {self.destination.id}", self.file_path)
            print(f"Encomenda criada no ponto {self.origin.id} com destino ao ponto {self.destination.id}")

    def stop(self):
        """Método para parar a thread após o pacote ser entregue"""
        controle.log_event(f"Encomenda {self.id} finalizada", self.file_path)
        print(f"Encomenda {self.id} finalizada")


# Função de ponto de redistribuição
class RedistributionPoint(threading.Thread):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.queue = []
        self.lock = threading.Lock()          # Controla acesso à fila de pacotes
        self.vehicle_lock = threading.Lock()  # Controla acesso exclusivo ao ponto por veículo
        self.sem = threading.Semaphore(0)
        self.running = True

    def run(self):
        while self.running:
            time.sleep(0.5)  # Controla o ciclo da thread, pelo que entendi evita consumir 100% da CPU

# adiciona encomendas ao ponto de distribuicao (nao é o que carrega o veiculo)
    def add_package(self, package):
        try:
            with self.lock: #garantir acesso unico
                self.queue.append(package)
                self.sem.release()  # Incrementa o semáforo
                controle.packages_waiting += 1  # Atualiza o contador global
        except:
            print("tentativa de acesso para receber carga em ponto de redistribuicao ocupado, aguarde sua vez...")

# essa sim é o que faz um veiculo pegar uma encomenda
    def dispatch_package(self) -> type[Package] | None:
        try:
            with self.lock:  # Lock para garantir que a fila será manipulada de maneira consistente
                if self.sem.acquire(blocking=False):  # Verifica se há pacotes disponíveis
                    controle.packages_waiting -= 1
                    return self.queue.pop(0)  # Retira o pacote mais antigo da fila
            return None
        except:
            print("tentativa de acesso para receber carga em ponto de redistribuicao ocupado, aguarde sua vez...")

    def stop(self):
        print(f'ponto de redistribuicao {self.id} finalizado')
        self.running = False  # Permite parar a thread de forma controlada


# classe para os carros
class Vehicle(threading.Thread):
    def __init__(self, id, capacity: int, points: list[type[RedistributionPoint]]):
        super().__init__()
        self.id = id
        self.capacity = capacity
        self.points = points
        self.current_point = random.choice(self.points)
        self.load: list[type[Package]] = []
        self.file_path = f"Carro_{self.id}_log.txt"
        self.running = True

    def run(self):
        while self.running:

            # Verificar se o veículo está cheio
            if len(self.load) == self.capacity:
                # Se estiver, verifica se o ponto atual é o destino de alguma encomenda
                has_destination = any(package.destination == self.current_point for package in self.load)

                # Se nenhuma encomenda tem aquele ponto como destino
                if not has_destination:
                    # O veículo passa reto e vai para o próximo ponto
                    print(f"[{time.strftime('%H:%M:%S')}] Veículo {self.id} está passando reto pelo ponto {self.current_point.id}, sem encomendas com destino no ponto.")
                    controle.log_event(f"Veículo {self.id} está passando reto pelo ponto {self.current_point.id}, pois não há encomenda com destino aqui.", self.file_path)

                    # Vai para o próximo ponto
                    next_point = self.points[(self.points.index(self.current_point) + 1) % len(self.points)]
                    print(f"[{time.strftime('%H:%M:%S')}] Veículo {self.id} partindo do ponto {self.current_point.id} para o ponto {next_point.id}")
                    time.sleep(random.uniform(0.2, 2))  # Tempo de viagem entre os pontos
                    self.current_point = next_point
                    continue  # Não faz mais nada neste ciclo, continua para o próximo ponto

            # Se chegou até aqui, ou está cheio e tem destino, ou não está cheio
            try:
                with self.current_point.vehicle_lock:  # Trava o ponto de redistribuição

                    # Log da posição atual dos pacotes deste veículo
                    for package in self.load:
                        controle.log_event(f"Passando pelo ponto {self.current_point.id}, carga atual: {len(self.load)} / {self.capacity}", package.file_path)

                    # Carrega encomendas no ponto atual
                    for _ in range(self.capacity - len(self.load)):
                        package = self.current_point.dispatch_package()
                        if package:
                            self.load.append(package)
                            controle.log_event(f"Carregada encomenda {package.id} no veículo {self.id} no ponto {self.current_point.id}", package.file_path)
                            print(f"[{time.strftime('%H:%M:%S')}] Carregada encomenda {package.id} no veículo {self.id} no ponto {self.current_point.id}")
                            time.sleep(random.uniform(0.2, 1.5))  # Tempo de carregamento de cada encomenda
                        else:
                            break

                    # Descarrega encomendas no ponto de destino
                    for package in self.load[:]:
                        if package.destination == self.current_point:
                            controle.log_event(f"Encomenda {package.id} descarregada no ponto {self.current_point.id}", package.file_path)
                            print(f"Encomenda {package.id} descarregada no ponto {self.current_point.id}")
                            self.load.remove(package)
                            package.stop()  # Faz a thread do pacote parar corretamente
            except:
                controle.log_event(f"Pedido de acesso ao Ponto {self.current_point} pelo veiculo {self.id} bloqueado, aguarde...")
                print(f"Pedido de acesso ao Ponto {self.current_point} pelo veiculo {self.id} bloqueado, aguarde...")

            # Movimentação circular
            next_point = self.points[(self.points.index(self.current_point) + 1) % len(self.points)]
            print(f"[{time.strftime('%H:%M:%S')}] Veículo {self.id} partindo do ponto {self.current_point.id} para o ponto {next_point.id}")
            time.sleep(random.uniform(0.2, 1))  # Tempo de viagem entre pontos
            self.current_point = next_point

            # Verifica se ainda há encomendas a serem carregadas ou descarregadas deste carro
            if not self.load and controle.packages_waiting == 0:
                self.stop()

    def stop(self):
        self.running = False  # Parar a thread de forma manual


if __name__ == "__main__":
    pass
