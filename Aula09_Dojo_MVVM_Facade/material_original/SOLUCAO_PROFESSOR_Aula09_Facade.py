"""SOLUCAO DO PROFESSOR - Lab Facade (RecepcaoFacade). Nao distribuir antes.

A Facade nao implementa a regra de novo: ela ORQUESTRA os subsistemas que ja
existem, escondendo a ordem e o 'if' atras de um metodo so. Compare com
fazer_reserva_na_mao(): e a mesma sequencia, mas agora morando num lugar unico.

Delimitacao (GIRIDHAR): em Python, se a orquestracao e trivial, uma funcao de
modulo ja serve de facade - nao precisa de classe. A classe se justifica quando
ha estado/varios subsistemas a segurar. E cuidado: facade NAO impede o acesso
direto aos subsistemas (nao e encapsulamento forte) - ela so oferece um caminho
simples. Nao deixe virar um 'God object' que faz tudo.
"""
class RecepcaoFacade:
    def __init__(self, disponibilidade, tarifa, reservas, notificador):
        self._disp = disponibilidade
        self._tar = tarifa
        self._rep = reservas
        self._notif = notificador

    def reservar(self, quarto, hospede, noites):
        if not self._disp.esta_livre(quarto):
            return {"ok": False, "motivo": "indisponivel"}
        total = self._tar.calcular(quarto, noites)
        rid = self._rep.gravar(quarto, hospede, noites, total)
        self._notif.enviar(hospede, f"Reserva {rid} confirmada - total R$ {total:.2f}")
        return {"ok": True, "reserva_id": rid, "total": total}
