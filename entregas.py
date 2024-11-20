import threading
import os 
import random
import time

from classes import RedistributionPoint
from classes import Vehicle
from classes import Package
import controle

# Inicialização da simulação com argumentos
def initialize_simulation(S, C, P, A):
    print("---- | Iniciando a simulação da rede de entregas | ----\n")
    
    # Cria um total de S pontos de redistribuição, cada um contendo a id 'i'
    for i in range(S):
        print(f'Criando o ponto {i+1} de distribuicao')
        redistribution_point = RedistributionPoint(i)
        controle.redistribution_points.append(redistribution_point)
        redistribution_point.start()  # Iniciar a thread
    
    print(f'{S} pontos criados e inicializados com sucesso')
    
    # Cria C veículos, cada um com id 'i' e a capacidade A
    for i in range(C):
        print(f'Criando veiculo {i+1}')
        vehicle = Vehicle(i, A, controle.redistribution_points)
        controle.vehicles.append(vehicle)
        vehicle.start()  # Inicia a thread do veículo
    
    print(f'Veiculos criados com sucesso')
    
    # Cria as P encomendas
    for i in range(P):
        print(f'Criando encomenda {i+1}')
        #gerar encomenda em algum ponto aleatorio 
        origin = random.choice(controle.redistribution_points)
        destination = random.choice([p for p in controle.redistribution_points if p != origin])
        Package(i, origin, destination)  # Inicia o pacote como uma thread
    
    print(f'Encomendas criadas com sucessos')
    
    # Aguarda todos os veículos finalizarem
    for v in controle.vehicles:
        print(f'for de veiculos finalizando')
        v.join()
    
    print(f'depois do for de veiculos')
    
    # Aguarda todos os pontos de redistribuição finalizarem
    for point in controle.redistribution_points:
        print(f'ponto de redistribuicao {i+1} finalizado')
        point.stop()  # Para a thread de cada ponto de redistribuição
        point.join()  # Aguarda o término da thread do ponto de redistribuição
    
    print(f'pontos de redistribuicao finalizados')
    print("\nSimulação concluída.")


# Parâmetros de entrada
"""
S = pontos de distribuicao
C = veiculos disponiveis 
P = total de encomendas a serem entregues
A = espacos de carga para cada veiculos (todas as encomendas ocupam exatamente 1 espaco de carga)

P >> A >> C

"""

if __name__ == "__main__":
    controle.setup_global()
    S, C, P, A = 5, 2, 5, 2  # Configurações menores para teste
    initialize_simulation(S, C, P, A)