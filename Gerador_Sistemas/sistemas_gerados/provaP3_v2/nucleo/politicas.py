"""
Cooperativa Citrícola — STRATEGY (Aula 05): as regras de destino da fruta.

ANTES (nucleo/antes_politicas.py): CobrancaAntiga.valor() com if/elif por destino da fruta.
DEPOIS (aqui):
  * cada regra é uma classe com o MESMO método aplicar(base) → estratégias intercambiáveis;
  * Cobranca (o CONTEXTO) recebe a estratégia e DELEGA — nenhum if;
  * política nova = classe nova; Cobranca não muda (OCP).
Quando NÃO usar: uma regra só, que nunca varia — uma função ou constante basta.
"""


class PoliticaIndustria:
    """Política Indústria (destino da fruta): aplica o fator 1.0 sobre o total."""

    FATOR = 1.0

    def aplicar(self, base):
        # Cada política conhece só a SUA regra; quem usa não precisa de if.
        return round(base * self.FATOR, 2)


class PoliticaMesa:
    """Política Mesa (destino da fruta): aplica o fator 1.25 sobre o total."""

    FATOR = 1.25

    def aplicar(self, base):
        # Cada política conhece só a SUA regra; quem usa não precisa de if.
        return round(base * self.FATOR, 2)


class PoliticaExportacao:
    """Política Exportação (destino da fruta): aplica o fator 1.4 sobre o total."""

    FATOR = 1.4

    def aplicar(self, base):
        # Cada política conhece só a SUA regra; quem usa não precisa de if.
        return round(base * self.FATOR, 2)


class PoliticaRefugo:
    """Política NOVA (Refugo): criada SEM tocar em Cobranca — aberto p/ estender, fechado p/ modificar."""

    FATOR = 0.3

    def aplicar(self, base):
        # Cada política conhece só a SUA regra; quem usa não precisa de if.
        return round(base * self.FATOR, 2)


class Cobranca:
    """CONTEXTO do Strategy: TEM-UM item (LoteCitros) e TEM-UMA política."""

    def __init__(self, item, politica):
        self.item = item
        # Sem "_": trocar a política de fora é permitido (ex.: cliente mudou de categoria).
        self.politica = politica

    def valor(self):
        """Delega: pede à política que se aplique ao total. Não sabe QUAL política é."""
        return self.politica.aplicar(self.item.total)


class CobrancaComFuncao:
    """Variante pythônica (GIRIDHAR): a estratégia pode ser qualquer FUNÇÃO f(base) -> valor."""

    def __init__(self, item, politica):
        self.item = item
        self.politica = politica

    def valor(self):
        return self.politica(self.item.total)
