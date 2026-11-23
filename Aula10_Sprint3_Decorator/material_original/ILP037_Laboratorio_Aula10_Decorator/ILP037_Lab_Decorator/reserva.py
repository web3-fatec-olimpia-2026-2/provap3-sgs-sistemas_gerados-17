"""
Decorator - servicos extras numa reserva do Resort de Olimpia.

Uma reserva tem um preco e uma descricao. O hospede pode somar EXTRAS, em
qualquer combinacao: cafe da manha, transfer do aeroporto, late checkout.

>>> O SMELL <<<
A funcao preco_com_extras() resolve os extras com uma pilha de flags e ifs.
Cada extra novo obriga a:
  - acrescentar um parametro booleano,
  - acrescentar mais um if,
  - e mexer em TODO lugar que chama a funcao.
E a descricao do que foi contratado fica espalhada, difcil de montar junto
com o preco. Nao da para combinar extras dinamicamente.

(A alternativa ingenua seria uma classe por combinacao - ReservaComCafe,
ReservaComCafeETransfer, ReservaComCafeTransferELate... - uma explosao de
subclasses. Pior ainda.)

>>> SEU TRABALHO <<<
Aplicar o Decorator: cada extra vira um "embrulho" que recebe uma reserva
(ou outro extra ja embrulhado), implementa a MESMA interface (preco /
descricao) e ACRESCENTA a sua parte. Assim voce empilha extras em qualquer
ordem e combinacao, em tempo de execucao.

As classes ComCafeDaManha, ComTransfer e ComLateCheckout abaixo estao
INCOMPLETAS de proposito (so herdam a delegacao da base). Os testes batem
nelas e ficam VERMELHOS ate voce implementar preco() e descricao().
"""


# ---------------------------------------------------------------------------
# O COMPONENTE BASE - uma reserva simples (nao mexa)
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
# A BASE DOS DECORADORES - embrulha uma reserva e, por padrao, DELEGA
# (nao mexa; as subclasses e que acrescentam)
# ---------------------------------------------------------------------------
class ServicoExtra:
    def __init__(self, reserva):
        self._reserva = reserva

    def preco(self) -> float:
        return self._reserva.preco()

    def descricao(self) -> str:
        return self._reserva.descricao()


# ---------------------------------------------------------------------------
# OS DECORADORES QUE VOCE VAI COMPLETAR - hoje so delegam (VERMELHO)
# ---------------------------------------------------------------------------
class ComCafeDaManha(ServicoExtra):
    """TODO: somar PRECO ao preco e acrescentar ' + cafe da manha' a descricao."""
    PRECO = 40.0
    # TODO: implemente preco() e descricao()


class ComTransfer(ServicoExtra):
    """TODO: somar PRECO ao preco e acrescentar ' + transfer' a descricao."""
    PRECO = 80.0
    # TODO: implemente preco() e descricao()


class ComLateCheckout(ServicoExtra):
    """TODO: somar PRECO ao preco e acrescentar ' + late checkout' a descricao."""
    PRECO = 60.0
    # TODO: implemente preco() e descricao()


# ---------------------------------------------------------------------------
# O SMELL: flags e ifs (a alternativa que o Decorator substitui)
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
