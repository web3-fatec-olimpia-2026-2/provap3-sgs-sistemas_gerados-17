"""
Sistema Exemplo — FACADE (Aula 09): um balcão único na frente de vários subsistemas.

ORDEM: disponibilidade → cálculo → cobrança → registro → notificação.
A fachada ORQUESTRA e DELEGA; a regra de cada passo continua no seu subsistema.
Quando NÃO usar: 1–2 passos num lugar só (uma função basta). Cuidado com o God object.
Facade ≠ Adapter: aqui são VÁRIOS subsistemas e uma interface NOVA e simples.
"""
from nucleo.atendimento_base import PagamentoRecusado


class AtendimentoFacade:
    def __init__(self, disponibilidade, calculadora, pagamentos, registro, notificador):
        # Segura os subsistemas (injetados → dá para testar com fakes).
        self._disponibilidade = disponibilidade
        self._calculadora = calculadora
        self._pagamentos = pagamentos
        self._registro = registro
        self._notificador = notificador

    def concluir(self, recurso, item):
        """Ponto de entrada único: o cliente não conhece os subsistemas nem a ordem."""
        # 1) Verifica ANTES de cobrar: não se cobra o que não se pode entregar.
        if not self._disponibilidade.esta_disponivel(recurso):
            return {"ok": False, "motivo": "indisponivel"}
        # 2) Quanto custa — quem sabe é a Calculadora.
        valor = self._calculadora.calcular(item)
        # 3) Cobra; se recusar, para aqui (nada registrado, ninguém notificado).
        try:
            tx = self._pagamentos.cobrar(item.cliente, valor)
        except PagamentoRecusado:
            return {"ok": False, "motivo": "pagamento recusado"}
        # 4) e 5) Só com o pagamento garantido: registra e avisa.
        protocolo = self._registro.registrar(recurso, item, valor)
        self._notificador.enviar(item.cliente, f"Protocolo {protocolo} confirmado - recurso {recurso} - total R$ {valor:.2f}")
        return {"ok": True, "protocolo": protocolo, "tx": tx, "total": valor}
