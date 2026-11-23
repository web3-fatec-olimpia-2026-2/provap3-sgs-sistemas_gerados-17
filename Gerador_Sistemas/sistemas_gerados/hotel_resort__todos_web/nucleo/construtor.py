"""
Hotel Resort — BUILDER (GoF · criação): montar a Reserva PASSO A PASSO, com nomes.

ANTES (nucleo/antes_construtor.py): nova_reserva_antiga(...) com todos os argumentos na ORDEM —
dois números trocados de lugar passam despercebidos e não há receitas prontas.
DEPOIS (aqui):
  * ReservaBuilder tem um com_<campo>() por atributo; cada um devolve o próprio builder
    (interface FLUENTE: b.com_x(...).com_y(...));
  * construir() confere o que falta e só então cria a Reserva (os setters validam cada valor);
  * DiretorDeReserva guarda "receitas" de montagem que se repetem.
Quando NÃO usar: poucos campos — em Python, argumentos NOMEADOS já resolvem a ordem.
"""
from nucleo.entidades import Reserva

OBRIGATORIOS = ['hospede', 'quarto', 'diarias', 'valor_diaria']


class ReservaBuilder:
    """BUILDER: junta os valores aos poucos e cria a Reserva no final."""

    def __init__(self):
        self._valores = {}

    def com_hospede(self, valor):
        """Informa hospede e devolve o PRÓPRIO builder (para encadear)."""
        self._valores["hospede"] = valor
        return self


    def com_quarto(self, valor):
        """Informa quarto e devolve o PRÓPRIO builder (para encadear)."""
        self._valores["quarto"] = valor
        return self


    def com_diarias(self, valor):
        """Informa diarias e devolve o PRÓPRIO builder (para encadear)."""
        self._valores["diarias"] = valor
        return self


    def com_valor_diaria(self, valor):
        """Informa valor_diaria e devolve o PRÓPRIO builder (para encadear)."""
        self._valores["valor_diaria"] = valor
        return self


    def com_observacao(self, valor):
        """Informa observacao e devolve o PRÓPRIO builder (para encadear)."""
        self._valores["observacao"] = valor
        return self

    def faltando(self):
        """Campos obrigatórios que ainda não foram informados."""
        return [campo for campo in OBRIGATORIOS if campo not in self._valores]

    def construir(self):
        """Cria a Reserva. Faltou campo → ValueError dizendo QUAL; valor inválido → o setter barra."""
        falta = self.faltando()
        if falta:
            raise ValueError(f"faltam campos: {', '.join(falta)}")
        return Reserva(**self._valores)


class DiretorDeReserva:
    """DIRETOR: receitas de montagem que se repetem (o passo a passo fica num lugar só)."""

    PADRAO = {'quarto': 101, 'diarias': 2, 'valor_diaria': 200.0}

    def basico(self, hospede):
        builder = ReservaBuilder().com_hospede(hospede)
        for campo, valor in self.PADRAO.items():
            getattr(builder, f"com_{campo}")(valor)
        return builder.construir()
