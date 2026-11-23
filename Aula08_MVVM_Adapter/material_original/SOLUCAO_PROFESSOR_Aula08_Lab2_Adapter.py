"""
SOLUCAO DO PROFESSOR -- Lab 2 (Adapter)

Nao distribua antes da correcao. Para validar: substitua a classe
NeonReservaAdapter vazia por esta, remova o 'if' do ReservaService
(versao abaixo) e rode os testes -> todos verdes.

A essencia do Adapter:
  - ALVO  (Target)  : ReservaRepository (salvar/buscar) -- o que a app espera
  - ADAPTADO (Adaptee): ClienteNeon (execute/fetch_one) -- interface alheia
  - ADAPTER         : NeonReservaAdapter -- fala a lingua da app por fora e
                      traduz para a lingua do Neon por dentro.

Delimitacao em Python (GIRIDHAR): quando voce controla as duas pontas e as
interfaces sao parecidas, duck typing ja resolve -- o Adapter so se justifica
quando o Adaptee e codigo de terceiro cuja assinatura voce NAO pode mudar.
E exatamente o caso de um driver de banco.
"""


class NeonReservaAdapter:
    def __init__(self, cliente):
        self._cliente = cliente

    def salvar(self, reserva: dict) -> int:
        resposta = self._cliente.execute("INSERT_RESERVA", reserva)
        return int(resposta["ticket"])          # traduz {'ticket': n} -> n

    def buscar(self, reserva_id: int) -> dict | None:
        resposta = self._cliente.fetch_one(reserva_id)
        if resposta is None:
            return None
        return resposta["row"]                   # desembrulha {'row': {...}}


# ReservaService LIMPO: um repo so, zero 'if de banco'.
class ReservaServiceLimpo:
    def __init__(self, repo):
        self._repo = repo

    def confirmar(self, reserva: dict) -> int:
        return self._repo.salvar(reserva)
