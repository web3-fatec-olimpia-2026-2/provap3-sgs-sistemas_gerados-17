"""ANTES — o smell do Singleton: cada parte do sistema cria a SUA configuração (e elas divergem)."""


class ConfiguracaoAntiga:
    def __init__(self):
        self.moeda = "R$"
        self.taxa_servico = 0.0


# Cada módulo guardava a sua cópia:
CONFIG_DO_CAIXA = ConfiguracaoAntiga()
CONFIG_DO_RELATORIO = ConfiguracaoAntiga()


def total_no_caixa(item):
    return round(item.total * (1 + CONFIG_DO_CAIXA.taxa_servico), 2)


def total_no_relatorio(item):
    return round(item.total * (1 + CONFIG_DO_RELATORIO.taxa_servico), 2)
