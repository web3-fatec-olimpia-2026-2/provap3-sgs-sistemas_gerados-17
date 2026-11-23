"""
Aula 09 — Laboratório Facade na recepção do Resort (RESOLVIDO).

Fazer uma reserva envolve QUATRO subsistemas, na ordem:
  1. Disponibilidade (está livre?)  2. Tarifa (quanto custa?)
  3. Reservas (grava, devolve nº)   4. Notificador (avisa o hóspede)

ANTES: o cliente (fazer_reserva_na_mao) conhecia os 4, a ORDEM e a REGRA.
DEPOIS: RecepcaoFacade.reservar(...) — um balcão único; o cliente só fala com ele.
"""


# ---------------------------------------------------------------------------
# OS QUATRO SUBSISTEMAS (prontos — não mexer)
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
        self.enviadas = []

    def enviar(self, hospede, mensagem):
        self.enviadas.append((hospede, mensagem))


# ---------------------------------------------------------------------------
# A FACADE
# ---------------------------------------------------------------------------
class RecepcaoFacade:
    """Balcão único na frente dos quatro subsistemas.

    - __init__ SEGURA os subsistemas (por isso a fachada é uma classe e não só uma função:
      há estado/configuração a guardar — delimitação de GIRIDHAR).
    - reservar() ORQUESTRA: chama cada subsistema na ordem certa.
    - Ela NÃO reimplementa a regra de nenhum (não calcula tarifa, não grava dicionário):
      só delega. Se começar a executar regra, vira "God object".
    """

    def __init__(self, disponibilidade, tarifa, reservas, notificador):
        self._disp = disponibilidade
        self._tar = tarifa
        self._rep = reservas
        self._notif = notificador

    def reservar(self, quarto, hospede, noites):
        # 1) regra de fluxo: ocupado → aborta ANTES de gravar/notificar
        if not self._disp.esta_livre(quarto):
            return {"ok": False, "motivo": "indisponivel"}
        # 2) quanto custa — quem sabe é a Tarifa
        total = self._tar.calcular(quarto, noites)
        # 3) grava — quem sabe é Reservas
        rid = self._rep.gravar(quarto, hospede, noites, total)
        # 4) avisa — quem sabe é o Notificador
        self._notif.enviar(hospede, f"Reserva {rid} confirmada - total R$ {total:.2f}")
        return {"ok": True, "reserva_id": rid, "total": total}


# ---------------------------------------------------------------------------
# ANTES: o cliente orquestrava na mão (mantido para comparação)
# ---------------------------------------------------------------------------
def fazer_reserva_na_mao(quarto, hospede, noites, disp, tar, rep, notif):
    if not disp.esta_livre(quarto):
        return {"ok": False, "motivo": "indisponivel"}
    total = tar.calcular(quarto, noites)
    rid = rep.gravar(quarto, hospede, noites, total)
    notif.enviar(hospede, f"Reserva {rid} confirmada - total R$ {total:.2f}")
    return {"ok": True, "reserva_id": rid, "total": total}


# ---------------------------------------------------------------------------
# Extra (delimitação): "às vezes uma função basta" — orquestração simples, sem estado
# próprio, pode ser uma função de módulo. Aqui ela recebe tudo pronto e só delega.
# ---------------------------------------------------------------------------
def criar_recepcao_padrao(ocupados=()):
    """Monta a fachada com os subsistemas reais — quem usa nem precisa saber quais são."""
    return RecepcaoFacade(Disponibilidade(ocupados), Tarifa(), Reservas(), Notificador())
