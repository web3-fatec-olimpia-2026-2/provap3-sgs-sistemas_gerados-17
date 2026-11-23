"""
Facade na recepcao do Resort de Olimpia.

Fazer uma reserva hoje envolve QUATRO subsistemas, chamados na ordem certa:
  1. Disponibilidade - o quarto esta livre?
  2. Tarifa          - quanto custa (diaria x noites)?
  3. Reservas        - grava e devolve um numero
  4. Notificador     - avisa o hospede

>>> O SMELL <<<
Veja fazer_reserva_na_mao() la embaixo: o codigo cliente conhece os QUATRO
subsistemas, a ORDEM entre eles e a REGRA (se nao esta livre, aborta). Cada tela
nova que precisar reservar vai repetir essa orquestracao inteira. Se amanha entrar
um 5o passo (ex.: emitir nota), todo mundo que reserva tem que mudar.

>>> SEU TRABALHO <<<
Construir uma FACADE: RecepcaoFacade.reservar(quarto, hospede, noites). Ela esconde
a orquestracao atras de UM metodo simples. O cliente passa a chamar so a facade.

A classe RecepcaoFacade abaixo esta vazia de proposito: os testes batem nela e
ficam VERMELHOS.
"""


# ---------------------------------------------------------------------------
# OS QUATRO SUBSISTEMAS (ja prontos - nao mexa neles)
# ---------------------------------------------------------------------------
class Disponibilidade:
    def __init__(self, ocupados):
        self._ocupados = set(ocupados)

    def esta_livre(self, quarto) -> bool:
        return quarto not in self._ocupados


class Tarifa:
    TABELA = {101: 200.0, 201: 500.0, 301: 1200.0}

    def calcular(self, quarto, noites) -> float:
        return self.TABELA[quarto] * noites


class Reservas:
    def __init__(self):
        self._dados = {}
        self._seq = 1

    def gravar(self, quarto, hospede, noites, total) -> int:
        rid = self._seq
        self._dados[rid] = {"quarto": quarto, "hospede": hospede,
                            "noites": noites, "total": total}
        self._seq += 1
        return rid

    def buscar(self, rid):
        return self._dados.get(rid)


class Notificador:
    def __init__(self):
        self.enviadas = []     # historico, para o teste conferir

    def enviar(self, hospede, mensagem):
        self.enviadas.append((hospede, mensagem))


# ---------------------------------------------------------------------------
# A FACADE QUE VOCE VAI CONSTRUIR - hoje vazia (VERMELHO)
# ---------------------------------------------------------------------------
class RecepcaoFacade:
    """
    Esconde a orquestracao dos quatro subsistemas atras de um metodo so.

    TODO (voce):
      __init__: receber e guardar os quatro subsistemas.
      reservar(quarto, hospede, noites):
        - se o quarto NAO esta livre: devolver {"ok": False, "motivo": "indisponivel"}
          (sem gravar, sem notificar)
        - se esta livre: calcular total, gravar, notificar o hospede com a mensagem
          f"Reserva {rid} confirmada - total R$ {total:.2f}", e devolver
          {"ok": True, "reserva_id": rid, "total": total}
    """

    def __init__(self, disponibilidade, tarifa, reservas, notificador):
        pass  # TODO

    def reservar(self, quarto, hospede, noites):
        pass  # TODO


# ---------------------------------------------------------------------------
# O SMELL: o cliente orquestra os quatro na mao
# ---------------------------------------------------------------------------
def fazer_reserva_na_mao(quarto, hospede, noites, disp, tar, rep, notif):
    if not disp.esta_livre(quarto):          # regra + subsistema 1
        return {"ok": False, "motivo": "indisponivel"}
    total = tar.calcular(quarto, noites)      # subsistema 2
    rid = rep.gravar(quarto, hospede, noites, total)  # subsistema 3
    notif.enviar(hospede, f"Reserva {rid} confirmada - total R$ {total:.2f}")  # 4
    return {"ok": True, "reserva_id": rid, "total": total}
