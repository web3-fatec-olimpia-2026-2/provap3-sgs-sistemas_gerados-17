"""
Sistema Exemplo — STRATEGY (Aula 05): as regras de tipo de cliente.

ANTES (nucleo/antes_politicas.py): CobrancaAntiga.valor() com if/elif por tipo de cliente.
DEPOIS (aqui):
  * cada regra é uma classe com o MESMO método aplicar(base) → estratégias intercambiáveis;
  * Cobranca (o CONTEXTO) recebe a estratégia e DELEGA — nenhum if;
  * política nova = classe nova; Cobranca não muda (OCP).
Quando NÃO usar: uma regra só, que nunca varia — uma função ou constante basta.
"""


class PoliticaComum:
    """Política Comum (tipo de cliente): aplica o fator 1.0 sobre o total."""

    FATOR = 1.0

    def aplicar(self, base):
        # Cada política conhece só a SUA regra; quem usa não precisa de if.
        return round(base * self.FATOR, 2)


class PoliticaEspecial:
    """Política Especial (tipo de cliente): aplica o fator 0.9 sobre o total."""

    FATOR = 0.9

    def aplicar(self, base):
        # Cada política conhece só a SUA regra; quem usa não precisa de if.
        return round(base * self.FATOR, 2)


class PoliticaParceiro:
    """Política Parceiro (tipo de cliente): aplica o fator 0.8 sobre o total."""

    FATOR = 0.8

    def aplicar(self, base):
        # Cada política conhece só a SUA regra; quem usa não precisa de if.
        return round(base * self.FATOR, 2)


class PoliticaVip:
    """Política NOVA (Vip): criada SEM tocar em Cobranca — aberto p/ estender, fechado p/ modificar."""

    FATOR = 0.5

    def aplicar(self, base):
        # Cada política conhece só a SUA regra; quem usa não precisa de if.
        return round(base * self.FATOR, 2)


class Cobranca:
    """CONTEXTO do Strategy: TEM-UM item (Atendimento) e TEM-UMA política."""

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
