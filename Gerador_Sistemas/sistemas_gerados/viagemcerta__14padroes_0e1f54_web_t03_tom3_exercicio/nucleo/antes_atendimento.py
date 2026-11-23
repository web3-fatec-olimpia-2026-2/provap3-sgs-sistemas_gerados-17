"""ANTES — o smell do Facade: o CLIENTE orquestra os 5 subsistemas na mão (e cada tela repete)."""
from nucleo.atendimento_base import PagamentoRecusado


def atender_na_mao(recurso, item, disponibilidade, calculadora, pagamentos, registro, notificador):
    if not disponibilidade.esta_disponivel(recurso):
        return {"ok": False, "motivo": "indisponivel"}
    valor = calculadora.calcular(item)
    try:
        tx = pagamentos.cobrar(item.viajante, valor)
    except PagamentoRecusado:
        return {"ok": False, "motivo": "pagamento recusado"}
    protocolo = registro.registrar(recurso, item, valor)
    notificador.enviar(item.viajante, f"Protocolo {protocolo} confirmado - voo {recurso} - total R$ {valor:.2f}")
    return {"ok": True, "protocolo": protocolo, "tx": tx, "total": valor}
