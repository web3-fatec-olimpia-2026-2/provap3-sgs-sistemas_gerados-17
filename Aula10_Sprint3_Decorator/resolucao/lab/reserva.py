"""
Aula 10 — Laboratório Decorator: serviços extras numa reserva (RESOLVIDO).

ANTES: preco_com_extras(diaria, noites, cafe=False, transfer=False, late=False)
       → cada extra novo = mais um parâmetro, mais um if, e mexer em quem chama.
       (Uma classe por combinação seria pior: explosão de subclasses.)

DEPOIS (Decorator, GoF estrutural):
  - Componente:      ReservaBase  (preco / descricao)
  - Decorador base:  ServicoExtra (EMBRULHA uma reserva e, por padrão, DELEGA)
  - Decoradores:     ComCafeDaManha, ComTransfer, ComLateCheckout
                     → mesma interface; chamam o de DENTRO e SOMAM a sua parte.
Como a interface por fora é IGUAL à de dentro, um embrulho pode embrulhar outro → EMPILHA.
"""


# ---------------------------------------------------------------------------
# COMPONENTE BASE (o "presente")
# ---------------------------------------------------------------------------
class ReservaBase:
    def __init__(self, diaria, noites):
        self.diaria = diaria
        self.noites = noites

    def preco(self) -> float:
        return self.diaria * self.noites

    def descricao(self) -> str:
        return f"Reserva {self.noites} noite(s)"


# ---------------------------------------------------------------------------
# DECORADOR BASE: guarda o objeto embrulhado e repassa as chamadas.
# ---------------------------------------------------------------------------
class ServicoExtra:
    def __init__(self, reserva):
        # "reserva" pode ser uma ReservaBase OU outro ServicoExtra já embrulhado:
        # tanto faz, porque os dois respondem preco() e descricao().
        self._reserva = reserva

    def preco(self) -> float:
        return self._reserva.preco()

    def descricao(self) -> str:
        return self._reserva.descricao()


# ---------------------------------------------------------------------------
# DECORADORES CONCRETOS: cada um = uma camada de papel em volta.
# Receita: resultado_de_dentro + a_minha_parte. O de dentro NÃO muda.
# ---------------------------------------------------------------------------
class ComCafeDaManha(ServicoExtra):
    PRECO = 40.0

    def preco(self):
        return self._reserva.preco() + self.PRECO

    def descricao(self):
        return self._reserva.descricao() + " + cafe da manha"


class ComTransfer(ServicoExtra):
    PRECO = 80.0

    def preco(self):
        return self._reserva.preco() + self.PRECO

    def descricao(self):
        return self._reserva.descricao() + " + transfer"


class ComLateCheckout(ServicoExtra):
    PRECO = 60.0

    def preco(self):
        return self._reserva.preco() + self.PRECO

    def descricao(self):
        return self._reserva.descricao() + " + late checkout"


# ---------------------------------------------------------------------------
# Extra (mostra o "quando o Decorator ganha": o extra MUDA COMPORTAMENTO,
# não só soma número fixo). Desconto de 10% sobre TUDO que está dentro.
# Aqui a ORDEM importa: aplicar o desconto antes ou depois do transfer muda o total.
# ---------------------------------------------------------------------------
class ComDescontoFidelidade(ServicoExtra):
    def preco(self):
        return round(self._reserva.preco() * 0.90, 2)

    def descricao(self):
        return self._reserva.descricao() + " (-10% fidelidade)"


# ---------------------------------------------------------------------------
# ANTES (o smell) — mantido para comparar
# ---------------------------------------------------------------------------
def preco_com_extras(diaria, noites, cafe=False, transfer=False, late=False):
    total = diaria * noites
    if cafe:
        total += 40.0
    if transfer:
        total += 80.0
    if late:
        total += 60.0
    return total


# Delimitação (GIRIDHAR): se TODO extra fosse só "somar um número fixo", bastaria
#   total = base + sum(extra.valor for extra in extras)
# — uma lista resolve, Decorator seria cerimônia. E o @decorator do Python decora
# FUNÇÕES; o padrão Decorator decora OBJETOS. Mesma ideia de embrulhar, mecanismos diferentes.
