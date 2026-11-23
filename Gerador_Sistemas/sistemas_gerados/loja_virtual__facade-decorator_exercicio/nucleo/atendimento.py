# MODO EXERCÍCIO — nucleo/atendimento.py: implemente cada método (a resolução está em gabarito/nucleo/atendimento.py).
# Rode `python -m pytest` para conferir; `ALVO=gabarito python -m pytest` mostra o gabarito passando.
"""
Loja Virtual — FACADE (Aula 09): um balcão único na frente de vários subsistemas.

ORDEM: disponibilidade → cálculo → cobrança → registro → notificação.
A fachada ORQUESTRA e DELEGA; a regra de cada passo continua no seu subsistema.
Quando NÃO usar: 1–2 passos num lugar só (uma função basta). Cuidado com o God object.
Facade ≠ Adapter: aqui são VÁRIOS subsistemas e uma interface NOVA e simples.
"""
from nucleo.atendimento_base import PagamentoRecusado

class AtendimentoFacade:

    def __init__(self, disponibilidade, calculadora, pagamentos, registro, notificador):
        raise NotImplementedError('TODO: implemente __init__')

    def concluir(self, recurso, item):
        """Ponto de entrada único: o cliente não conhece os subsistemas nem a ordem."""
        raise NotImplementedError('TODO: implemente concluir')
