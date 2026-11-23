"""Aula 02 — Reserva protegida com @property (construída com TDD).

Reproduz o exercício dos vídeos da Aula 02 / branch `aula-02` do repositório de referência,
CORRIGINDO o limite de `diarias` (o repositório usa `<= 1`, que rejeita 1 diária).

Regras do negócio:
    - valor_diaria nunca é negativo
    - diarias é no mínimo 1
    - total = diarias × valor_diaria (calculado na hora, nunca guardado)
"""


class Reserva:
    def __init__(self, hospede, quarto, diarias, valor_diaria):
        # hospede e quarto NÃO têm regra nesta aula → atributos simples.
        # Colocar @property neles seria "cerimônia" (critério antifachada).
        self.hospede = hospede
        self.quarto = quarto
        # Estas duas linhas NÃO gravam direto: como existe @property com setter
        # para esses nomes, o Python chama o setter → a validação roda já na criação.
        self.diarias = diarias
        self.valor_diaria = valor_diaria

    # ---------- valor_diaria ----------
    @property
    def valor_diaria(self):
        """GETTER: executado quando alguém LÊ r.valor_diaria."""
        return self._valor_diaria   # o dado real fica no atributo interno "_valor_diaria"

    @valor_diaria.setter
    def valor_diaria(self, novo):
        """SETTER: executado quando alguém ESCREVE r.valor_diaria = x. É a fechadura."""
        if novo < 0:
            raise ValueError("valor_diaria nao pode ser negativo")
        self._valor_diaria = novo

    # ---------- diarias ----------
    @property
    def diarias(self):
        return self._diarias

    @diarias.setter
    def diarias(self, novo):
        # Regra: "ao menos 1 diária". Por isso o teste é "< 1".
        # (Com "<= 1", como no repositório de referência, uma reserva de 1 noite seria barrada.)
        if novo < 1:
            raise ValueError("diarias deve ser no minimo 1")
        self._diarias = novo

    # ---------- total (calculado) ----------
    @property
    def total(self):
        """Property CALCULADA e SÓ LEITURA (não tem setter).

        Se o total fosse guardado num atributo, mudar `diarias` o deixaria desatualizado.
        Calculando na hora, ele sempre concorda com os outros dois dados.
        """
        return self.diarias * self.valor_diaria
