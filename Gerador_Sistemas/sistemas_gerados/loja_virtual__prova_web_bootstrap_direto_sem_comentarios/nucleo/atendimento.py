from nucleo.atendimento_base import PagamentoRecusado


class AtendimentoFacade:
    def __init__(self, disponibilidade, calculadora, pagamentos, registro, notificador):
        self._disponibilidade = disponibilidade
        self._calculadora = calculadora
        self._pagamentos = pagamentos
        self._registro = registro
        self._notificador = notificador

    def concluir(self, recurso, item):
        if not self._disponibilidade.esta_disponivel(recurso):
            return {"ok": False, "motivo": "indisponivel"}
        valor = self._calculadora.calcular(item)
        try:
            tx = self._pagamentos.cobrar(item.cliente, valor)
        except PagamentoRecusado:
            return {"ok": False, "motivo": "pagamento recusado"}
        protocolo = self._registro.registrar(recurso, item, valor)
        self._notificador.enviar(item.cliente, f"Protocolo {protocolo} confirmado - produto {recurso} - total R$ {valor:.2f}")
        return {"ok": True, "protocolo": protocolo, "tx": tx, "total": valor}
