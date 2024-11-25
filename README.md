# SO
 gerenciamento de entregas usando threads
 
 Cada ponto de redistribuição tem uma variável lock (do tipo threading.Lock()) e um semáforo (sem) para controlar o acesso ao ponto e a fila de encomendas.
 
 O lock é usado para garantir que apenas um veículo acesse o ponto de redistribuição ao mesmo tempo, evitando que múltiplos veículos tentem carregar ou descarregar encomendas de forma concorrente.

 Quando um veículo está carregando ou descarregando encomendas, ele precisa adquirir o lock do ponto de redistribuição para garantir que ele tenha acesso exclusivo ao ponto de redistribuição. Isso é feito com o comando: --- with self.current_point.lock ---

 SEM é usado para controlar a quantidade de encomendas em espera no ponto de redistribuição.

 SEM é liberado quando uma encomenda é adicionada ao ponto de redistribuição:

 Quando um veículo tenta receber uma encomenda, ele chama o método dispatch_package do ponto de redistribuição, que tenta adquirir o semáforo. Se o semáforo tiver um valor maior que 0 (tem encomendas disponíveis), o semáforo é decrementado, e o veículo carrea a encomenda

# Resumindo:
 Locking: Cada ponto de redistribuição tem um lock para garantir que somente um veículo possa carregar ou descarregar encomendas de cada vez.

 Semáforo: O semáforo é usado para controlar a quantidade de encomendas que um ponto pode fornecer a um veículo, garantindo que o veículo só pegue uma encomenda quando houver uma disponível no ponto.

 Sendo assim, a lógica lock + semaforo garante que o acesso aos pontos de redistribuicao seja sequencial e controlado, evitando que múltiplos tentem acessar o ponto ao mesmo tempo e garantindo que as encomendas sejam retiradas de forma controlada.


