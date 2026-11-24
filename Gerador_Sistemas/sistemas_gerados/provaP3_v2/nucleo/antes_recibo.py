"""ANTES — o smell do SRP: a classe que faz tudo (três motivos para mudar)."""
from nucleo.entidades import LoteCitros


class LoteCitrosFazTudo(LoteCitros):
    """Herda dados e total (negócio) e ainda FORMATA (apresentação) e SALVA (infraestrutura)."""

    def formatar_recibo(self):
        return (f"RECIBO - Cooperativa Citrícola\n{self.cooperado}\n"
                f"{self.caixas} caixa(s)\nTotal: R$ {self.total:.2f}")

    def salvar_em_arquivo(self, caminho):
        with open(caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write(self.formatar_recibo())
