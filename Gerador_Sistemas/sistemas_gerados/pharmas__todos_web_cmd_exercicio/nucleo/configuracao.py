"""
Pharmas — SINGLETON (GoF · criação): UMA configuração para o sistema inteiro.

ANTES (nucleo/antes_configuracao.py): cada parte criava a sua ConfiguracaoAntiga(); mudar a taxa
numa não mudava nas outras → caixa e relatório cobrando valores diferentes.
DEPOIS (aqui):
  * __new__ devolve SEMPRE o mesmo objeto (guardado no atributo de CLASSE _instancia);
  * quem precisa chama Configuracao() e recebe a única que existe;
  * reiniciar() existe só para os testes começarem do zero.
Quando NÃO usar: em Python um MÓDULO já é único — uma variável no módulo resolve sem cerimônia.
Singleton é estado global escondido: prefira injetar a dependência quando der.
"""


class Configuracao:
    """SINGLETON: a única configuração do Pharmas (moeda e taxa de serviço)."""

    _instancia = None  # o objeto único fica guardado na CLASSE

    def __new__(cls):
        # __new__ CRIA o objeto (roda antes do __init__): aqui decidimos devolver o que já existe.
        if cls._instancia is None:
            instancia = super().__new__(cls)
            instancia.moeda = "R$"
            instancia.taxa_servico = 0.0
            cls._instancia = instancia
        return cls._instancia

    @classmethod
    def reiniciar(cls):
        """Apaga a instância única (usado pelos testes para começar do zero)."""
        cls._instancia = None


def total_com_taxa(item):
    """Total da Pharm + a taxa de serviço da configuração ÚNICA."""
    return round(item.total * (1 + Configuracao().taxa_servico), 2)


def formatar(valor):
    """Valor com a moeda da configuração ÚNICA (quem calcula e quem formata leem a mesma)."""
    return f"{Configuracao().moeda} {valor:.2f}"
