"""
Subsistemas PRONTOS do Facade (não mexer). Cada um anota no `log` o que fez, para os
testes conferirem a ORDEM da orquestração.
"""


class PagamentoRecusado(Exception):
    pass


class Disponibilidade:
    def __init__(self, indisponiveis, log):
        self._indisponiveis = set(indisponiveis)
        self._log = log

    def esta_disponivel(self, recurso):
        self._log.append("disponibilidade.esta_disponivel")
        return recurso not in self._indisponiveis


class Calculadora:
    def __init__(self, log):
        self._log = log

    def calcular(self, item):
        self._log.append("calculadora.calcular")
        return item.total


class Pagamentos:
    def __init__(self, log, recusar=False):
        self._log = log
        self._recusar = recusar

    def cobrar(self, cliente, valor):
        self._log.append("pagamentos.cobrar")
        if self._recusar:
            raise PagamentoRecusado("cartão recusado")
        return f"TX-{cliente}-{valor:.2f}"


class Registro:
    def __init__(self, log):
        self._log = log
        self._dados = {}
        self._seq = 1

    def registrar(self, recurso, item, valor):
        self._log.append("registro.registrar")
        protocolo = self._seq
        self._dados[protocolo] = {"recurso": recurso, "cliente": item.cooperado, "valor": valor}
        self._seq += 1
        return protocolo

    def buscar(self, protocolo):
        return self._dados.get(protocolo)


class Notificador:
    def __init__(self, log):
        self._log = log
        self.enviadas = []

    def enviar(self, cliente, mensagem):
        self._log.append("notificador.enviar")
        self.enviadas.append((cliente, mensagem))
